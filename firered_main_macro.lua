-- FireRed Reset + Starter Selection + Screenshot
-- Python-controlled start with debugging

local RESET_DELAY = 1800
local SCREENSHOT_DELAY = 90

local SCREENSHOT_PATH = "C:/Users/Sotoc/OneDrive/Desktop/CofC/Fall 2026/CSIS690/Class Repo/690/.idea/CV Shiny Hunting/pictures/firered_capture.png"

-- Each variance is generated once per run and added to all later steps.
-- Steps 2 and 3 replay recent events and receive no additional variance.
local schedule = {
    {frame = 0, key = C.GBA_KEY.A, maxVariance = 1800},
    {frame = 207, key = C.GBA_KEY.A, maxVariance = 1800},
    {frame = 367, key = C.GBA_KEY.A, maxVariance = 0},
    {frame = 508, key = C.GBA_KEY.A, maxVariance = 0},
    {frame = 599, key = C.GBA_KEY.A, maxVariance = 600},
    {frame = 858, key = C.GBA_KEY.A, maxVariance = 600},
    {frame = 1111, key = C.GBA_KEY.A, maxVariance = 600},
    {frame = 1298, key = C.GBA_KEY.A, maxVariance = 3600},
    {frame = 1888, key = C.GBA_KEY.DOWN, maxVariance = 0},
    {frame = 1955, key = C.GBA_KEY.A, maxVariance = 0},
    {frame = 2235, key = C.GBA_KEY.A, maxVariance = 0},
    {frame = 2634, key = C.GBA_KEY.START, maxVariance = 0},
    {frame = 2720, key = C.GBA_KEY.A, maxVariance = 0},
    {frame = 2803, key = C.GBA_KEY.A, maxVariance = 0},
    {frame = 2874, key = C.GBA_KEY.A, maxVariance = 0}
}

local frame = -1
local nextStep = 1
local heldKey = nil
local macroStarted = false
local macroCompleted = false
local currentVariance = 0

local function startMacro()
    console:log("startMacro() called")

    currentVariance = 0

    for i, action in ipairs(schedule) do
        local addedVariance = math.random(0, action.maxVariance)
        currentVariance = currentVariance + addedVariance
        action.variance = addedVariance
        action.targetFrame = action.frame + currentVariance
    end

    frame = -1
    nextStep = 1
    heldKey = nil
    macroStarted = true
    macroCompleted = false

    console:log("Attempting emulator reset...")
    emu:reset()
    console:log("FireRed reset initiated.")

    for i, action in ipairs(schedule) do
        console:log("Step " .. (i - 1) .. ": +" .. action.variance ..
            " frames; target frame " .. action.targetFrame)
    end

    console:log("Total cumulative variance: " .. currentVariance .. " frames")
end

-- TCP server for Python commands
local server = socket.bind("127.0.0.1", 8765)
server:listen(5)

console:log("Waiting for Python START command...")

callbacks:add("frame", function()

    local client = server:accept()

    if client then
        console:log("Client connected")

        local command = client:receive(1024)

        if command then
            console:log("Received: " .. command)
            console:log("Command length: " .. #command)
            console:log("Matches START: " .. tostring(command == "START"))
            console:log("Macro started: " .. tostring(macroStarted))

            if command == "START" and not macroStarted then
                startMacro()
            end
        else
            console:log("No command data received.")
        end

        client:close()
    end

    if not macroStarted or macroCompleted then
        return
    end

    frame = frame + 1

    if heldKey ~= nil then
        emu:clearKey(heldKey)
        heldKey = nil
    end

    if frame < RESET_DELAY then
        return
    end

    local macroFrame = frame - RESET_DELAY

    if nextStep <= #schedule then
        local action = schedule[nextStep]

        if macroFrame >= action.targetFrame then
            emu:addKey(action.key)
            heldKey = action.key

            console:log("Step " .. (nextStep - 1) ..
                " executed at macro frame " .. macroFrame)

            nextStep = nextStep + 1
        end

    elseif heldKey == nil then
        if macroFrame >= schedule[#schedule].targetFrame + SCREENSHOT_DELAY then
            macroCompleted = true

            emu:screenshot(SCREENSHOT_PATH)

            console:log("FireRed reset macro completed!")
            console:log("Screenshot captured.")
        end
    end
end)
