--Test lua command
local server = nil

local function checkCommand()
    if server == nil then
        return
    end

    local client = server:accept()

    if client then
        console:log("Client connected")

        local command = client:receive(1024)

        if command then
            console:log("Received: " .. command)
        end

        client:close()
    end
end

server = socket.bind("127.0.0.1", 8765)
server:listen(5)

callbacks:add("frame", checkCommand)

console:log("Waiting for Python command...")