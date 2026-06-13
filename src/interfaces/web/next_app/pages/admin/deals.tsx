import { useState, useEffect } from "react"
import axios from "axios"
import { useSession } from "next-auth/react"

interface Deal {
  id: number
  name: string
  amount: number
  stage: string
}

export default function DealsPage() {
  const { data: session } = useSession()
  const [deals, setDeals] = useState<Deal[]>([])

  useEffect(() => {
    axios.get("/api/crm/deals", { headers: { Authorization: `Bearer ${session?.accessToken}` } })
      .then(res => setDeals(res.data))
  }, [session])

  const moveStage = async (id: number, stage: string) => {
    await axios.put(`/api/crm/deals/${id}/stage`, { stage }, {
      headers: { Authorization: `Bearer ${session?.accessToken}` }
    })
    // refresh
  }

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">مدیریت معاملات</h1>
      <div className="grid grid-cols-1 gap-4">
        {deals.map(deal => (
          <div key={deal.id} className="border p-4 rounded flex justify-between items-center">
            <div>
              <h3 className="font-bold">{deal.name}</h3>
              <p>{deal.amount} تومان</p>
              <span className="text-sm text-gray-500">{deal.stage}</span>
            </div>
            <div className="flex gap-2">
              <button onClick={() => moveStage(deal.id, "qualified")} className="bg-blue-500 text-white px-2 py-1 text-sm rounded">Qualify</button>
              <button onClick={() => moveStage(deal.id, "closed_won")} className="bg-green-500 text-white px-2 py-1 text-sm rounded">Won</button>
              <button onClick={() => moveStage(deal.id, "closed_lost")} className="bg-red-500 text-white px-2 py-1 text-sm rounded">Lost</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
