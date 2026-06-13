import { useSession, signIn, signOut } from "next-auth/react"
import { useState } from "react"
import axios from "axios"

export default function Home() {
  const { data: session } = useSession()
  const [menuTree, setMenuTree] = useState(null)

  const fetchMenu = async () => {
    try {
      const res = await axios.get("/api/admin/menus/tree", {
        headers: { Authorization: `Bearer ${session?.accessToken}` }
      })
      setMenuTree(res.data)
    } catch (err) {
      console.error(err)
    }
  }

  if (!session) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <button onClick={() => signIn("credentials")} className="rounded bg-blue-500 px-4 py-2 text-white">
          ورود به پنل مالک
        </button>
      </div>
    )
  }

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold">TEOS Admin Panel</h1>
      <p>خوش آمدید، {session.user?.name}</p>
      <button onClick={() => signOut()} className="mt-4 rounded bg-red-500 px-4 py-2 text-white">
        خروج
      </button>
      <div className="mt-8">
        <button onClick={fetchMenu} className="rounded bg-green-500 px-4 py-2 text-white">
          بارگذاری منو
        </button>
        {menuTree && <pre>{JSON.stringify(menuTree, null, 2)}</pre>}
      </div>
    </div>
  )
}
