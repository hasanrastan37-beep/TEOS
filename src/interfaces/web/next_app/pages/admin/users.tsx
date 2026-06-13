import { useEffect, useState } from "react"
import axios from "axios"
import { useSession } from "next-auth/react"

interface User {
  id: number
  telegram_id: number
  full_name: string
  role: string
  is_blocked: boolean
}

export default function UsersPage() {
  const { data: session } = useSession()
  const [users, setUsers] = useState<User[]>([])
  const [search, setSearch] = useState("")
  const [loading, setLoading] = useState(false)

  const fetchUsers = async () => {
    setLoading(true)
    try {
      const res = await axios.get(`/api/admin/users?search=${search}`, {
        headers: { Authorization: `Bearer ${session?.accessToken}` }
      })
      setUsers(res.data)
    } catch (err) {
      console.error(err)
    }
    setLoading(false)
  }

  useEffect(() => {
    if (session) fetchUsers()
  }, [session, search])

  const updateUser = async (id: number, data: Partial<User>) => {
    await axios.put(`/api/admin/users/${id}`, data, {
      headers: { Authorization: `Bearer ${session?.accessToken}` }
    })
    fetchUsers()
  }

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">مدیریت کاربران</h1>
      <div className="flex mb-4 gap-2">
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="جستجوی نام یا یوزرنیم"
          className="border rounded px-3 py-1 w-64"
        />
        <button onClick={fetchUsers} className="bg-blue-500 text-white px-4 py-1 rounded">جستجو</button>
      </div>
      <table className="w-full border">
        <thead>
          <tr className="bg-gray-100">
            <th className="border p-2">شناسه تلگرام</th>
            <th className="border p-2">نام</th>
            <th className="border p-2">نقش</th>
            <th className="border p-2">وضعیت</th>
            <th className="border p-2">عملیات</th>
          </tr>
        </thead>
        <tbody>
          {users.map((u) => (
            <tr key={u.id}>
              <td className="border p-2">{u.telegram_id}</td>
              <td className="border p-2">{u.full_name}</td>
              <td className="border p-2">{u.role}</td>
              <td className="border p-2">{u.is_blocked ? "مسدود" : "فعال"}</td>
              <td className="border p-2">
                <button
                  onClick={() => updateUser(u.id, { is_blocked: !u.is_blocked })}
                  className="bg-red-500 text-white px-2 py-1 text-sm rounded mr-1"
                >
                  {u.is_blocked ? "رفع مسدودیت" : "مسدود"}
                </button>
                {u.role !== "owner" && (
                  <select
                    value={u.role}
                    onChange={(e) => updateUser(u.id, { role: e.target.value })}
                    className="border rounded px-1 py-1 text-sm"
                  >
                    <option value="user">کاربر عادی</option>
                    <option value="admin_music">ادمین موزیک</option>
                    <option value="admin_vpn">ادمین سرویس</option>
                  </select>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
