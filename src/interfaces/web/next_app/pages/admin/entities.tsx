import { useState, useEffect } from "react"
import axios from "axios"

interface EntityDef {
  id: number
  name: string
  fields_schema: any[]
}

export default function EntityBuilderPage() {
  const [entities, setEntities] = useState<EntityDef[]>([])
  const [newName, setNewName] = useState("")
  const [fields, setFields] = useState([{ name: "", type: "string", required: false }])

  useEffect(() => {
    axios.get("/api/entity-builder/definitions").then(res => setEntities(res.data))
  }, [])

  const addField = () => setFields([...fields, { name: "", type: "string", required: false }])
  const updateField = (idx: number, key: string, value: any) => {
    const updated = [...fields]
    updated[idx] = { ...updated[idx], [key]: value }
    setFields(updated)
  }

  const createEntity = async () => {
    await axios.post("/api/entity-builder/definitions", { name: newName, fields_schema: fields })
    setNewName("")
    setFields([{ name: "", type: "string", required: false }])
    const res = await axios.get("/api/entity-builder/definitions")
    setEntities(res.data)
  }

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Entity Builder</h1>
      <div className="mb-6 border p-4 rounded">
        <input value={newName} onChange={e => setNewName(e.target.value)} placeholder="نام موجودیت" className="border rounded px-3 py-1 mb-2" />
        {fields.map((f, idx) => (
          <div key={idx} className="flex gap-2 mb-2 items-center">
            <input value={f.name} onChange={e => updateField(idx, "name", e.target.value)} placeholder="نام فیلد" className="border rounded px-2 py-1 w-32" />
            <select value={f.type} onChange={e => updateField(idx, "type", e.target.value)} className="border rounded px-2 py-1">
              <option value="string">رشته</option>
              <option value="integer">عدد صحیح</option>
              <option value="email">ایمیل</option>
              <option value="boolean">بله/خیر</option>
            </select>
            <label className="flex items-center gap-1 text-sm">
              <input type="checkbox" checked={f.required} onChange={e => updateField(idx, "required", e.target.checked)} />
              الزامی
            </label>
          </div>
        ))}
        <button onClick={addField} className="text-blue-500 text-sm">+ افزودن فیلد</button>
        <br />
        <button onClick={createEntity} className="bg-green-500 text-white px-4 py-1 rounded mt-2">ایجاد موجودیت</button>
      </div>
      <h2 className="text-xl font-semibold mb-2">موجودیت‌های موجود</h2>
      <ul>
        {entities.map(e => (
          <li key={e.id}>{e.name} ({e.fields_schema.length} فیلد)</li>
        ))}
      </ul>
    </div>
  )
}
