import { useState, useEffect } from "react"
import axios from "axios"

interface MenuNode {
  id: number
  key: string
  label: string
  children: MenuNode[]
}

export default function MenuBuilder() {
  const [tree, setTree] = useState<MenuNode | null>(null)

  useEffect(() => {
    axios.get("/api/admin/menus/tree", { headers: { Authorization: `Bearer ` + (window as any).__NEXT_DATA__?.props?.session?.accessToken } })
      .then(res => setTree(res.data))
      .catch(console.error)
  }, [])

  const addNode = async (parentKey: string) => {
    const label = prompt("نام گره:")
    const key = prompt("کلید (یکتا):")
    if (!label || !key) return
    await axios.post("/api/admin/menus/node", { key, label, parent_key: parentKey }, {
      headers: { Authorization: `Bearer ` + (window as any).__NEXT_DATA__?.props?.session?.accessToken }
    })
    // رفرش
  }

  const renderTree = (node: MenuNode) => (
    <li key={node.id}>
      <span>{node.label} ({node.key})</span>
      <button onClick={() => addNode(node.key)} className="ml-2 text-xs bg-green-500 text-white px-1 rounded">+</button>
      {node.children?.length > 0 && (
        <ul className="ml-4">{node.children.map(renderTree)}</ul>
      )}
    </li>
  )

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">منو ساز</h1>
      {tree ? <ul>{renderTree(tree)}</ul> : <p>در حال بارگذاری...</p>}
    </div>
  )
}
