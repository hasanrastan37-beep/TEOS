import { useState, useEffect } from "react"
import axios from "axios"
import { useSession } from "next-auth/react"

interface Campaign {
  id: number
  name: string
  type: string
  status: string
  total_sent: number
}

export default function CampaignsPage() {
  const { data: session } = useSession()
  const [campaigns, setCampaigns] = useState<Campaign[]>([])

  useEffect(() => {
    axios.get("/api/marketing/campaigns", { headers: { Authorization: `Bearer ${session?.accessToken}` } })
      .then(res => setCampaigns(res.data))
  }, [session])

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">کمپین‌های بازاریابی</h1>
      <table className="w-full border">
        <thead>
          <tr className="bg-gray-100">
            <th className="border p-2">نام</th>
            <th className="border p-2">نوع</th>
            <th className="border p-2">وضعیت</th>
            <th className="border p-2">ارسال‌ها</th>
          </tr>
        </thead>
        <tbody>
          {campaigns.map(c => (
            <tr key={c.id}>
              <td className="border p-2">{c.name}</td>
              <td className="border p-2">{c.type}</td>
              <td className="border p-2">{c.status}</td>
              <td className="border p-2">{c.total_sent}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
