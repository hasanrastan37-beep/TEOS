import { useEffect, useState } from "react"
import axios from "axios"
import { useSession } from "next-auth/react"

interface Transaction {
  id: number
  type: string
  amount: number
  status: string
  description: string
}

export default function TransactionsPage() {
  const { data: session } = useSession()
  const [txs, setTxs] = useState<Transaction[]>([])

  const fetchPending = async () => {
    const res = await axios.get("/api/admin/transactions/pending", {
      headers: { Authorization: `Bearer ${session?.accessToken}` }
    })
    setTxs(res.data)
  }

  useEffect(() => {
    if (session) fetchPending()
  }, [session])

  const approve = async (id: number) => {
    await axios.post(`/api/admin/transactions/${id}/approve`, {}, {
      headers: { Authorization: `Bearer ${session?.accessToken}` }
    })
    fetchPending()
  }

  const reject = async (id: number) => {
    await axios.post(`/api/admin/transactions/${id}/reject`, { reason: "رد توسط ادمین" }, {
      headers: { Authorization: `Bearer ${session?.accessToken}` }
    })
    fetchPending()
  }

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">تراکنش‌های در انتظار</h1>
      <table className="w-full border">
        <thead>
          <tr className="bg-gray-100">
            <th className="border p-2">شناسه</th>
            <th className="border p-2">نوع</th>
            <th className="border p-2">مبلغ</th>
            <th className="border p-2">توضیحات</th>
            <th className="border p-2">عملیات</th>
          </tr>
        </thead>
        <tbody>
          {txs.map((tx) => (
            <tr key={tx.id}>
              <td className="border p-2">{tx.id}</td>
              <td className="border p-2">{tx.type}</td>
              <td className="border p-2">{tx.amount} تومان</td>
              <td className="border p-2">{tx.description}</td>
              <td className="border p-2">
                <button onClick={() => approve(tx.id)} className="bg-green-500 text-white px-2 py-1 text-sm rounded mr-1">تأیید</button>
                <button onClick={() => reject(tx.id)} className="bg-red-500 text-white px-2 py-1 text-sm rounded">رد</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
