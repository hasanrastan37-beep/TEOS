-- Rule evaluation in Lua for embedded high-performance tasks
function evaluate(rule, context)
   if rule.type == "condition" then
      local field = context[rule.field]
      if rule.operator == "eq" then return field == rule.value
      elseif rule.operator == "gt" then return field > rule.value
      end
   end
   return false
end

-- تست
local ctx = { age = 30 }
local r = { type = "condition", field = "age", operator = "gt", value = 18 }
print(evaluate(r, ctx))  -- true
