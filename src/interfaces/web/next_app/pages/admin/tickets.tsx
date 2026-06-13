import { useState, useEffect } from "react"
import axios from "axios"

interface Message {
  id: number
  sender_id: number
  content: string
  is_admin_reply: boolean
  created_at: string
}

interface Ticket {
  id: number
  subject: string
  status: string
  priority: string
  messages: Message[]
}

export default function TicketManagement() {
  const [tickets, setTickets] = useState<Ticket[]>([])
  const [selected, setSelected] = useState<Ticket | null>(null)
  const [replyText, setReplyText] = useState("")

  useEffect(() => {
    axios.get("/api/admin/tickets", { headers: { Authorization: "Bearer ..." } })
      .then(res => setTickets(res.data))
  }, [])

  const openTicket = (ticket: Ticket) => {
    axios.get(`/api/admin/tickets/${ticket.id}/messages`, { headers: { Authorization: "Bearer ..." } })
      .then(res => { ticket.messages = res.data; setSelected(ticket) })
  }

  const sendReply = async () => {
    if (!selected || !replyText) return
    await axios.post(`/api/admin/tickets/${selected.id}/reply`, { content: replyText }, { headers: { Authorization: "Bearer ..." } })
    setReplyText("")
    openTicket(selected)
  }

  return (
    <div className="p-8 flex gap-4">
      <div className="w-1/3 border rounded p-4">
        <h2 className="text-xl font-bold mb-2">تیکت‌ها</h2>
        {tickets.map(t => (
          <div key={t.id} className={`p-2 mb-1 cursor-pointer rounded ${selected?.id === t.id ? 'bg-blue-100' : 'bg-gray-50'}`} onClick={() => openTicket(t)}>
            <div className="font-bold">{t.subject}</div>
            <div className="text-sm">{t.status} | {t.priority}</div>
          </div>
        ))}
      </div>
      <div className="flex-1 border rounded p-4">
        {selected ? (
          <>
            <h2 className="text-xl font-bold">{selected.subject}</h2>
            <div className="h-96 overflow-y-auto border my-2 p-2">
              {selected.messages?.map(msg => (
                <div key={msg.id} className={`my-2 p-2 rounded ${msg.is_admin_reply ? 'bg-green-100 ml-4' : 'bg-white mr-4'}`}>
                  <div className="text-xs text-gray-500">{new Date(msg.created_at).toLocaleString()}</div>
                  <div>{msg.content}</div>
                </div>
              ))}
            </div>
            <div className="flex gap-2">
              <input value={replyText} onChange={(e) => setReplyText(e.target.value)} className="flex-1 border rounded px-3 py-1" placeholder="پاسخ..." />
              <button onClick={sendReply} className="bg-blue-500 text-white px-4 py-1 rounded">ارسال</button>
            </div>
          </>
        ) : <p>یک تیکت انتخاب کنید</p>}
      </div>
    </div>
  )
}
