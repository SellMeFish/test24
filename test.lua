--// SelfwareLibrary.lua
--// Vollständige, moderne UI-Library mit Keysystem, Discord Auto-Join,
--// Notifications, Tabs, Buttons, Paragraph, Color Picker usw.
--// PC & Mobile Support, Executor Detection dynamisch, 2 Themes, Lucide Icons.

local Selfware = {}
Selfware.__index = Selfware

-----------------------
-- Services & Locals --
-----------------------
local Players = game:GetService("Players")
local UserInputService = game:GetService("UserInputService")
local HttpService = game:GetService("HttpService")
local LocalPlayer = Players.LocalPlayer

-- Kurze Hilfs-Funktion zum geschützten Parenten (Synapse etc.)
local function protectUI(obj)
    if syn and syn.protect_gui then
        syn.protect_gui(obj)
        obj.Parent = game:GetService("CoreGui")
    else
        -- Fallback
        obj.Parent = LocalPlayer:WaitForChild("PlayerGui")
    end
end

-- Executor Detection (dynamisch, nicht nur hard-coded)
local executorList = {
    { Check = function() return syn and syn.protect_gui end, Name = "Synapse X" },
    { Check = function() return type(getexecutorname) == "function" end, Name = (getexecutorname and getexecutorname()) },
    { Check = function() return type(identifyexecutor) == "function" end, Name = (identifyexecutor and identifyexecutor()) },
    { Check = function() return Wave end, Name = "Wave" },
    { Check = function() return KRNL_LOADED end, Name = "KRNL" },
}
local function detectExecutor()
    for _, execData in pairs(executorList) do
        local success, result = pcall(execData.Check)
        if success and result then
            return "Using " .. (execData.Name or "an Executor")
        end
    end
    return "Using Unknown"
end
local ExecutorName = detectExecutor()

-- Lucide Icon (Beispielhaftes Dictionary)
-- Du kannst hier beliebig mehr Icons mappen (Name -> Roblox AssetId)
local LucideIcons = {
    ["alert-triangle"] = "rbxassetid://12974878581", -- nur Beispiel
    ["heart"] = "rbxassetid://12974881277", -- nur Beispiel
    ["sun"] = "rbxassetid://12974882119",   -- nur Beispiel
    ["moon"] = "rbxassetid://12974882669", -- nur Beispiel
    -- Füge hier weitere hinzu!
}

--------------------------------
-- Themes (DarkSnow / WhiteSun) --
--------------------------------
local Themes = {
    DarkSnow = {
        BackgroundColor = Color3.fromRGB(30, 30, 30),
        TitleBarColor = Color3.fromRGB(40, 40, 40),
        TextColor = Color3.fromRGB(255, 255, 255),
        AccentColor = Color3.fromRGB(0, 255, 255),
        Symbol = "❄️",
        NotificationColor = Color3.fromRGB(50, 50, 50),
    },
    WhiteSun = {
        BackgroundColor = Color3.fromRGB(245, 245, 245),
        TitleBarColor = Color3.fromRGB(220, 220, 220),
        TextColor = Color3.fromRGB(30, 30, 30),
        AccentColor = Color3.fromRGB(255, 196, 0),
        Symbol = "☀️",
        NotificationColor = Color3.fromRGB(200, 200, 200),
    }
}

Selfware.DefaultTheme = "DarkSnow"

-----------------------------------
-- Discord Auto-Join Einstellung --
-----------------------------------
-- Beispiel-Aufbau:
-- Discord = {
--   Enabled = false,
--   Invite = "noinvitelink",
--   RememberJoins = true
-- }

--------------------------------
-- Key System (lokaler Ansatz) --
--------------------------------
-- Du kannst das ausbauen, z.B. mit HTTP-Check oder DB-Abgleich.
-- Hier: Lokale "keys.txt" + Abfrage.

-------------------------------------------
-- Konfigurations-Speicher (save / load) --
-------------------------------------------
local function SafeWriteFile(fileName, data)
    if writefile and isfile then
        pcall(function()
            writefile(fileName, data)
        end)
    end
end

local function SafeReadFile(fileName)
    if readfile and isfile and isfile(fileName) then
        local succ, content = pcall(readfile, fileName)
        if succ and content then
            return content
        end
    end
    return nil
end

--------------------------------
-- ScreenGui / Notification UI --
--------------------------------
local function createScreenGui()
    local screenGui = Instance.new("ScreenGui")
    screenGui.Name = "SelfwareScreenGui"
    screenGui.IgnoreGuiInset = true
    screenGui.ResetOnSpawn = false
    protectUI(screenGui)
    return screenGui
end

local function createNotificationHolder(parent)
    local holder = Instance.new("Frame")
    holder.Name = "NotificationHolder"
    holder.AnchorPoint = Vector2.new(1, 1)
    holder.Position = UDim2.new(1, -10, 1, -10)
    holder.Size = UDim2.new(0, 300, 0, 200)
    holder.BackgroundTransparency = 1
    holder.Parent = parent

    return holder
end

--------------------------------
-- Haupt: Library-Init-Funktion
--------------------------------
function Selfware:Init(config)
    config = config or {}
    self.Config = config

    -- Theme
    local themeName = config.Theme or Selfware.DefaultTheme
    self.Theme = Themes[themeName] or Themes.DarkSnow

    -- Discord Auto-Join
    self.DiscordConfig = config.Discord or {
        Enabled = false,
        Invite = "noinvitelink",
        RememberJoins = true
    }

    -- KeySystem
    self.KeySystem = config.KeySystem or {
        Enabled = false,
        KeyFile = "selfware_key.txt",
        ValidKeys = { "MY-SECRET-KEY", "ABC123" }, -- Beispiel
    }

    -- Executor Info
    self.ExecutorName = ExecutorName

    -- Erstellt ScreenGui + NotificationHolder
    self.ScreenGui = createScreenGui()
    self.NotificationHolder = createNotificationHolder(self.ScreenGui)

    -- Wenn KeySystem aktiviert -> warte bis Key valid
    if self.KeySystem.Enabled then
        local hasValidKey = false
        -- Prüfen, ob wir lokal schon einen Key gespeichert haben
        local savedKey = SafeReadFile(self.KeySystem.KeyFile)
        if savedKey and table.find(self.KeySystem.ValidKeys, savedKey) then
            hasValidKey = true
        end

        while not hasValidKey do
            -- Prompt UI (kleine Key-Eingabe)
            local keyFrame = Instance.new("Frame")
            keyFrame.Size = UDim2.new(0, 300, 0, 150)
            keyFrame.Position = UDim2.new(0.5, -150, 0.5, -75)
            keyFrame.AnchorPoint = Vector2.new(0.5, 0.5)
            keyFrame.BackgroundColor3 = self.Theme.BackgroundColor
            keyFrame.Parent = self.ScreenGui

            local corner = Instance.new("UICorner")
            corner.CornerRadius = UDim.new(0, 8)
            corner.Parent = keyFrame

            local title = Instance.new("TextLabel")
            title.Size = UDim2.new(1, 0, 0, 30)
            title.BackgroundTransparency = 1
            title.Text = "Enter Key"
            title.Font = Enum.Font.SourceSansSemibold
            title.TextSize = 18
            title.TextColor3 = self.Theme.TextColor
            title.Parent = keyFrame

            local input = Instance.new("TextBox")
            input.Size = UDim2.new(1, -20, 0, 30)
            input.Position = UDim2.new(0, 10, 0, 40)
            input.BackgroundColor3 = self.Theme.TitleBarColor
            input.Text = ""
            input.PlaceholderText = "Key"
            input.TextColor3 = self.Theme.TextColor
            input.Font = Enum.Font.SourceSans
            input.TextSize = 16
            input.Parent = keyFrame

            local corner2 = Instance.new("UICorner")
            corner2.CornerRadius = UDim.new(0, 4)
            corner2.Parent = input

            local confirmBtn = Instance.new("TextButton")
            confirmBtn.Size = UDim2.new(1, -20, 0, 30)
            confirmBtn.Position = UDim2.new(0, 10, 0, 80)
            confirmBtn.Text = "Confirm"
            confirmBtn.TextColor3 = self.Theme.TextColor
            confirmBtn.BackgroundColor3 = self.Theme.AccentColor
            confirmBtn.Font = Enum.Font.SourceSansBold
            confirmBtn.TextSize = 16
            confirmBtn.Parent = keyFrame

            local corner3 = Instance.new("UICorner")
            corner3.Parent = confirmBtn

            -- Warte Button Click
            local clicked = false
            confirmBtn.MouseButton1Click:Connect(function()
                local typedKey = input.Text
                if table.find(self.KeySystem.ValidKeys, typedKey) then
                    hasValidKey = true
                    -- speichern
                    SafeWriteFile(self.KeySystem.KeyFile, typedKey)
                else
                    self:Notify("Key System", "Invalid Key.", 3)
                end
                clicked = true
            end)

            -- Warte, bis Button geklickt wurde
            repeat task.wait() until clicked

            keyFrame:Destroy()
        end
    end

    -- Discord Join Check
    if self.DiscordConfig.Enabled and self.DiscordConfig.Invite ~= "noinvitelink" then
        local joinedFile = "selfware_discord_joined.txt"
        local hasJoinedBefore = SafeReadFile(joinedFile)
        if (not hasJoinedBefore or self.DiscordConfig.RememberJoins == false) then
            -- Sende Join Request (Executor abh. -> z.B. syn.request)
            -- Normalerweise: discord.gg/<Invite>
            local link = "https://discord.gg/"..self.DiscordConfig.Invite
            if syn and syn.request then
                syn.request({
                    Url = link,
                    Method = "GET"
                })
            elseif request then
                request({
                    Url = link,
                    Method = "GET"
                })
            end
            -- wir tun so, als hätte es geklappt
            SafeWriteFile(joinedFile, "Joined")
        end
    end

    return self
end

----------------------------------------
-- Notifications (Theme-basiert Frame) --
----------------------------------------
function Selfware:Notify(title, message, duration)
    duration = duration or 3
    local theme = self.Theme

    -- Haupt-Frame
    local noteFrame = Instance.new("Frame")
    noteFrame.Size = UDim2.new(1, 0, 0, 60)
    noteFrame.BackgroundColor3 = theme.NotificationColor
    noteFrame.BorderSizePixel = 0
    noteFrame.Parent = self.NotificationHolder

    local corner = Instance.new("UICorner")
    corner.CornerRadius = UDim.new(0, 6)
    corner.Parent = noteFrame

    -- Titel
    local titleLabel = Instance.new("TextLabel")
    titleLabel.Size = UDim2.new(1, -10, 0, 25)
    titleLabel.Position = UDim2.new(0, 5, 0, 2)
    titleLabel.BackgroundTransparency = 1
    titleLabel.Text = title
    titleLabel.Font = Enum.Font.SourceSansBold
    titleLabel.TextSize = 18
    titleLabel.TextColor3 = theme.TextColor
    titleLabel.TextXAlignment = Enum.TextXAlignment.Left
    titleLabel.Parent = noteFrame

    -- Message
    local msgLabel = Instance.new("TextLabel")
    msgLabel.Size = UDim2.new(1, -10, 0, 25)
    msgLabel.Position = UDim2.new(0, 5, 0, 25)
    msgLabel.BackgroundTransparency = 1
    msgLabel.Text = message
    msgLabel.Font = Enum.Font.SourceSans
    msgLabel.TextSize = 16
    msgLabel.TextColor3 = theme.TextColor
    msgLabel.TextXAlignment = Enum.TextXAlignment.Left
    msgLabel.Parent = noteFrame

    -- Verschieben alte Notifys nach oben
    for _, child in ipairs(self.NotificationHolder:GetChildren()) do
        if child:IsA("Frame") and child ~= noteFrame then
            child.Position = child.Position - UDim2.new(0, 0, 0, 65)
        end
    end

    -- Auto-Entfernen
    task.delay(duration, function()
        pcall(function()
            noteFrame:Destroy()
        end)
    end)
end

----------------------------------
-- CreateWindow (mit Tabs etc.) --
----------------------------------
function Selfware:CreateWindow(windowTitle)
    windowTitle = windowTitle or "Selfware Hub"
    local theme = self.Theme

    -- Haupt-GUI
    local mainFrame = Instance.new("Frame")
    mainFrame.Name = "MainWindow"
    mainFrame.Size = UDim2.new(0, 600, 0, 400)
    mainFrame.Position = UDim2.new(0.5, -300, 0.5, -200)
    mainFrame.AnchorPoint = Vector2.new(0.5, 0.5)
    mainFrame.BackgroundColor3 = theme.BackgroundColor
    mainFrame.Parent = self.ScreenGui

    local corner = Instance.new("UICorner")
    corner.CornerRadius = UDim.new(0, 8)
    corner.Parent = mainFrame

    -- TitelBar
    local titleBar = Instance.new("Frame")
    titleBar.Size = UDim2.new(1, 0, 0, 40)
    titleBar.BackgroundColor3 = theme.TitleBarColor
    titleBar.Parent = mainFrame

    local corner2 = Instance.new("UICorner")
    corner2.CornerRadius = UDim.new(0, 8)
    corner2.Parent = titleBar

    local titleLabel = Instance.new("TextLabel")
    titleLabel.Size = UDim2.new(1, -50, 1, 0)
    titleLabel.Position = UDim2.new(0, 10, 0, 0)
    titleLabel.BackgroundTransparency = 1
    titleLabel.Text = windowTitle.." | "..self.ExecutorName
    titleLabel.Font = Enum.Font.SourceSansSemibold
    titleLabel.TextSize = 20
    titleLabel.TextColor3 = theme.TextColor
    titleLabel.TextXAlignment = Enum.TextXAlignment.Left
    titleLabel.Parent = titleBar

    local themeSymbol = Instance.new("TextLabel")
    themeSymbol.Size = UDim2.new(0, 40, 0, 40)
    themeSymbol.BackgroundTransparency = 1
    themeSymbol.Text = theme.Symbol
    themeSymbol.TextSize = 25
    themeSymbol.Font = Enum.Font.SourceSansBold
    themeSymbol.TextColor3 = theme.TextColor
    themeSymbol.Parent = titleBar

    -- Minimale Draggability
    local dragging = false
    local dragStart, startPos
    titleBar.InputBegan:Connect(function(input)
        if input.UserInputType == Enum.UserInputType.MouseButton1 or input.UserInputType == Enum.UserInputType.Touch then
            dragging = true
            dragStart = input.Position
            startPos = mainFrame.Position
            input.Changed:Connect(function()
                if input.UserInputState == Enum.UserInputState.End then
                    dragging = false
                end
            end)
        end
    end)
    titleBar.InputChanged:Connect(function(input)
        if
            input.UserInputType == Enum.UserInputType.MouseMovement
            or input.UserInputType == Enum.UserInputType.Touch
        then
            if dragging then
                local delta = input.Position - dragStart
                mainFrame.Position = UDim2.new(
                    startPos.X.Scale,
                    startPos.X.Offset + delta.X,
                    startPos.Y.Scale,
                    startPos.Y.Offset + delta.Y
                )
            end
        end
    end)

    -- ContentFrame
    local contentFrame = Instance.new("Frame")
    contentFrame.Size = UDim2.new(1, 0, 1, -40)
    contentFrame.Position = UDim2.new(0, 0, 0, 40)
    contentFrame.BackgroundTransparency = 1
    contentFrame.Name = "ContentFrame"
    contentFrame.Parent = mainFrame

    local windowObject = {
        Library = self,
        MainFrame = mainFrame,
        TitleBar = titleBar,
        ContentFrame = contentFrame,
        Elements = {},
    }

    setmetatable(windowObject, {__index = Selfware})

    -- Du könntest hier direkt ein "SettingsTab" erstellen
    windowObject:CreateSettingsTab()

    return windowObject
end

-----------------------------------
-- Standard-Settings-Tab mit Keybind-Save/Load
-----------------------------------
function Selfware:CreateSettingsTab()
    -- Hier legen wir einfach mal einen Button an, der "Config speichern" aufruft
    -- Der Einfachheit halber: Ein ganz simpler Container im ContentFrame
    local frame = Instance.new("Frame")
    frame.Size = UDim2.new(1, 0, 0, 40)
    frame.BackgroundColor3 = self.Theme.TitleBarColor
    frame.Parent = self.ContentFrame

    local corner = Instance.new("UICorner")
    corner.CornerRadius = UDim.new(0, 6)
    corner.Parent = frame

    local label = Instance.new("TextLabel")
    label.Size = UDim2.new(1, -80, 1, 0)
    label.Position = UDim2.new(0, 10, 0, 0)
    label.BackgroundTransparency = 1
    label.TextColor3 = self.Theme.TextColor
    label.Text = "Settings / Keybinds saved to config.json"
    label.Font = Enum.Font.SourceSans
    label.TextSize = 16
    label.TextXAlignment = Enum.TextXAlignment.Left
    label.Parent = frame

    local saveBtn = Instance.new("TextButton")
    saveBtn.Size = UDim2.new(0, 60, 0, 30)
    saveBtn.Position = UDim2.new(1, -70, 0.5, -15)
    saveBtn.Text = "Save"
    saveBtn.TextColor3 = self.Theme.TextColor
    saveBtn.Font = Enum.Font.SourceSansBold
    saveBtn.TextSize = 14
    saveBtn.BackgroundColor3 = self.Theme.AccentColor
    saveBtn.Parent = frame

    local corner2 = Instance.new("UICorner")
    corner2.Parent = saveBtn

    saveBtn.MouseButton1Click:Connect(function()
        self:SaveConfig()
        self.Library:Notify("Settings", "Config saved!", 2)
    end)
end

function Selfware:SaveConfig()
    -- Sammle alle Values von Elements
    local toSave = {}
    for _, elementData in pairs(self.Elements) do
        if elementData.Type and elementData.Object then
            toSave[elementData.ID] = elementData.Value
        end
    end
    local encoded = HttpService:JSONEncode(toSave)
    SafeWriteFile("selfware_config.json", encoded)
end

function Selfware:LoadConfig()
    local data = SafeReadFile("selfware_config.json")
    if data then
        local decoded = nil
        pcall(function()
            decoded = HttpService:JSONDecode(data)
        end)
        if decoded then
            for id, value in pairs(decoded) do
                -- Falls Element existiert, updaten wir
                if self.Elements[id] then
                    local t = self.Elements[id].Type
                    if t == "Slider" then
                        self:UpdateSlider(id, value)
                    elseif t == "ColorPicker" then
                        self:UpdateColorPicker(id, value)
                    elseif t == "Dropdown" then
                        self:UpdateDropdown(id, value)
                    elseif t == "Keybind" then
                        self:UpdateKeybind(id, value)
                    elseif t == "Input" then
                        self:UpdateInput(id, value)
                    elseif t == "Button" or t == "Label" or t == "Paragraph" or t == "Divider" or t == "Section" then
                        -- i.d.R. haben die keinen "Value" – kann man ignorieren
                    end
                end
            end
        end
    end
end

---------------------
-- Element Helpers --
---------------------
local function makeUICorner(radius, parent)
    local c = Instance.new("UICorner")
    c.CornerRadius = UDim.new(0, radius)
    c.Parent = parent
end

local function createIcon(iconName, size, parent)
    local icon = Instance.new("ImageLabel")
    icon.BackgroundTransparency = 1
    icon.Size = UDim2.new(0, size or 24, 0, size or 24)
    if LucideIcons[iconName] then
        icon.Image = LucideIcons[iconName]
    else
        -- Fallback
        icon.Image = "rbxassetid://12974878581" -- z.B. alert-triangle
    end
    icon.Parent = parent
    return icon
end

-----------------------------------
-- Element: Label / Update Label --
-----------------------------------
function Selfware:CreateLabel(id, text)
    local label = Instance.new("TextLabel")
    label.Size = UDim2.new(1, -10, 0, 20)
    label.BackgroundTransparency = 1
    label.TextColor3 = self.Theme.TextColor
    label.Font = Enum.Font.SourceSans
    label.TextSize = 16
    label.TextXAlignment = Enum.TextXAlignment.Left
    label.Text = text
    label.Parent = self.ContentFrame

    self.Elements[id] = {
        ID = id,
        Type = "Label",
        Object = label,
        Value = text
    }
end

function Selfware:UpdateLabel(id, newText)
    local elem = self.Elements[id]
    if elem and elem.Type == "Label" then
        elem.Object.Text = newText
        elem.Value = newText
    end
end

---------------------------------------
-- Element: Paragraph / Update Para --
---------------------------------------
function Selfware:CreateParagraph(id, text)
    local label = Instance.new("TextLabel")
    label.Size = UDim2.new(1, -10, 0, 60)
    label.BackgroundTransparency = 1
    label.TextColor3 = self.Theme.TextColor
    label.Font = Enum.Font.SourceSans
    label.TextSize = 16
    label.TextXAlignment = Enum.TextXAlignment.Left
    label.TextYAlignment = Enum.TextYAlignment.Top
    label.TextWrapped = true
    label.Text = text
    label.Parent = self.ContentFrame

    self.Elements[id] = {
        ID = id,
        Type = "Paragraph",
        Object = label,
        Value = text
    }
end

function Selfware:UpdateParagraph(id, newText)
    local elem = self.Elements[id]
    if elem and elem.Type == "Paragraph" then
        elem.Object.Text = newText
        elem.Value = newText
    end
end

---------------------------------
-- Element: Button / Update it --
---------------------------------
function Selfware:CreateButton(id, text, callback, iconName)
    local btn = Instance.new("TextButton")
    btn.Size = UDim2.new(0, 150, 0, 30)
    btn.BackgroundColor3 = self.Theme.TitleBarColor
    btn.TextColor3 = self.Theme.TextColor
    btn.Font = Enum.Font.SourceSansBold
    btn.TextSize = 16
    btn.Text = text
    btn.Parent = self.ContentFrame
    makeUICorner(6, btn)

    if iconName then
        local icon = createIcon(iconName, 20, btn)
        icon.Position = UDim2.new(0, 5, 0.5, -10)
        btn.TextXAlignment = Enum.TextXAlignment.Right
        btn.Text = "     "..text
    end

    btn.MouseButton1Click:Connect(function()
        if callback then
            pcall(callback)
        end
    end)

    self.Elements[id] = {
        ID = id,
        Type = "Button",
        Object = btn,
        Value = text
    }
end

function Selfware:UpdateButton(id, newText)
    local elem = self.Elements[id]
    if elem and elem.Type == "Button" then
        elem.Object.Text = newText
        elem.Value = newText
    end
end

------------------------------------
-- Element: ColorPicker / Update --
------------------------------------
function Selfware:CreateColorPicker(id, defaultColor, callback)
    local frame = Instance.new("Frame")
    frame.Size = UDim2.new(0, 200, 0, 40)
    frame.BackgroundColor3 = self.Theme.TitleBarColor
    frame.Parent = self.ContentFrame
    makeUICorner(6, frame)

    local btn = Instance.new("TextButton")
    btn.Size = UDim2.new(0, 40, 0, 40)
    btn.BackgroundColor3 = defaultColor or Color3.new(1, 1, 1)
    btn.Text = ""
    btn.Parent = frame
    makeUICorner(6, btn)

    local label = Instance.new("TextLabel")
    label.Size = UDim2.new(1, -50, 1, 0)
    label.Position = UDim2.new(0, 50, 0, 0)
    label.BackgroundTransparency = 1
    label.TextColor3 = self.Theme.TextColor
    label.Font = Enum.Font.SourceSans
    label.TextSize = 16
    label.TextXAlignment = Enum.TextXAlignment.Left
    label.Text = "ColorPicker"
    label.Parent = frame

    local cpValue = defaultColor or Color3.new(1,1,1)

    btn.MouseButton1Click:Connect(function()
        -- Bei Klick könnte man z.B. ein kleines Popup zeigen
        -- Hier nur ein Example: Wir togglen die Farbe
        cpValue = Color3.new(math.random(), math.random(), math.random())
        btn.BackgroundColor3 = cpValue
        if callback then
            callback(cpValue)
        end
    end)

    self.Elements[id] = {
        ID = id,
        Type = "ColorPicker",
        Object = frame,
        Value = cpValue
    }
end

function Selfware:UpdateColorPicker(id, newColor)
    local elem = self.Elements[id]
    if elem and elem.Type == "ColorPicker" then
        local frame = elem.Object
        local btn = frame:FindFirstChildOfClass("TextButton")
        if btn then
            btn.BackgroundColor3 = newColor
        end
        elem.Value = newColor
    end
end

-----------------------------------------------
-- Element: Input / TextBox (Adaptive Input) --
-----------------------------------------------
function Selfware:CreateInput(id, placeholder, defaultText, callback)
    local box = Instance.new("TextBox")
    box.Size = UDim2.new(0, 200, 0, 30)
    box.BackgroundColor3 = self.Theme.TitleBarColor
    box.TextColor3 = self.Theme.TextColor
    box.Font = Enum.Font.SourceSans
    box.TextSize = 16
    box.PlaceholderText = placeholder or "Enter text..."
    box.Text = defaultText or ""
    box.Parent = self.ContentFrame
    makeUICorner(6, box)

    box.FocusLost:Connect(function(enterPressed)
        if enterPressed then
            if callback then
                callback(box.Text)
            end
        end
    end)

    self.Elements[id] = {
        ID = id,
        Type = "Input",
        Object = box,
        Value = defaultText or ""
    }
end

function Selfware:UpdateInput(id, newText)
    local elem = self.Elements[id]
    if elem and elem.Type == "Input" then
        elem.Object.Text = newText
        elem.Value = newText
    end
end

--------------------------------
-- Element: Dropdown / Update --
--------------------------------
function Selfware:CreateDropdown(id, list, defaultIndex, callback)
    local frame = Instance.new("Frame")
    frame.Size = UDim2.new(0, 200, 0, 30)
    frame.BackgroundColor3 = self.Theme.TitleBarColor
    frame.Parent = self.ContentFrame
    makeUICorner(6, frame)

    local label = Instance.new("TextLabel")
    label.Size = UDim2.new(1, -30, 1, 0)
    label.Position = UDim2.new(0, 5, 0, 0)
    label.BackgroundTransparency = 1
    label.TextColor3 = self.Theme.TextColor
    label.Font = Enum.Font.SourceSans
    label.TextSize = 16
    label.TextXAlignment = Enum.TextXAlignment.Left
    label.Text = list[defaultIndex or 1] or "Select"
    label.Parent = frame

    local btn = Instance.new("TextButton")
    btn.Size = UDim2.new(0, 30, 1, 0)
    btn.Position = UDim2.new(1, -30, 0, 0)
    btn.Text = "v"
    btn.TextColor3 = self.Theme.TextColor
    btn.BackgroundTransparency = 1
    btn.Parent = frame

    local dropOpen = false
    local dropFrame = Instance.new("Frame")
    dropFrame.Size = UDim2.new(1, 0, 0, #list * 25)
    dropFrame.Position = UDim2.new(0, 0, 1, 0)
    dropFrame.BackgroundColor3 = self.Theme.BackgroundColor
    dropFrame.Visible = false
    dropFrame.Parent = frame

    makeUICorner(6, dropFrame)

    for i, item in ipairs(list) do
        local option = Instance.new("TextButton")
        option.Size = UDim2.new(1, 0, 0, 25)
        option.Position = UDim2.new(0, 0, 0, (i-1)*25)
        option.BackgroundColor3 = self.Theme.TitleBarColor
        option.TextColor3 = self.Theme.TextColor
        option.Text = item
        option.Parent = dropFrame
        option.MouseButton1Click:Connect(function()
            label.Text = item
            if callback then
                callback(item)
            end
            dropOpen = false
            dropFrame.Visible = false
        end)
    end

    btn.MouseButton1Click:Connect(function()
        dropOpen = not dropOpen
        dropFrame.Visible = dropOpen
    end)

    self.Elements[id] = {
        ID = id,
        Type = "Dropdown",
        Object = frame,
        Value = list[defaultIndex or 1] or ""
    }
end

function Selfware:UpdateDropdown(id, newVal)
    local elem = self.Elements[id]
    if elem and elem.Type == "Dropdown" then
        local frame = elem.Object
        local label = frame:FindFirstChildOfClass("TextLabel")
        if label then
            label.Text = newVal
        end
        elem.Value = newVal
    end
end

function Selfware:ResetDropdown(id)
    local elem = self.Elements[id]
    if elem and elem.Type == "Dropdown" then
        local frame = elem.Object
        local label = frame:FindFirstChildOfClass("TextLabel")
        if label then
            label.Text = "Select"
        end
        elem.Value = ""
    end
end

---------------------------------------------
-- Element: Slider / Update (für Beispiel) --
---------------------------------------------
function Selfware:CreateSlider(id, minVal, maxVal, defaultVal, callback)
    local frame = Instance.new("Frame")
    frame.Size = UDim2.new(0, 200, 0, 40)
    frame.BackgroundColor3 = self.Theme.TitleBarColor
    frame.Parent = self.ContentFrame
    makeUICorner(6, frame)

    local valLabel = Instance.new("TextLabel")
    valLabel.Size = UDim2.new(1, 0, 0, 20)
    valLabel.BackgroundTransparency = 1
    valLabel.TextColor3 = self.Theme.TextColor
    valLabel.Font = Enum.Font.SourceSans
    valLabel.TextSize = 16
    valLabel.Text = tostring(defaultVal or 0)
    valLabel.Parent = frame

    local sliderBar = Instance.new("Frame")
    sliderBar.Size = UDim2.new(1, -10, 0, 5)
    sliderBar.Position = UDim2.new(0, 5, 0, 25)
    sliderBar.BackgroundColor3 = self.Theme.BackgroundColor
    sliderBar.Parent = frame

    local fillBar = Instance.new("Frame")
    fillBar.Size = UDim2.new(0, 0, 1, 0)
    fillBar.BackgroundColor3 = self.Theme.AccentColor
    fillBar.Parent = sliderBar

    local sliderValue = defaultVal or minVal or 0
    local function updateSlider(inputX)
        local barAbsSize = sliderBar.AbsoluteSize.X
        local barAbsPos = sliderBar.AbsolutePosition.X
        local pos = math.clamp(inputX - barAbsPos, 0, barAbsSize)
        fillBar.Size = UDim2.new(0, pos, 1, 0)
        local ratio = pos/barAbsSize
        local value = math.floor((minVal + (maxVal-minVal) * ratio))
        sliderValue = value
        valLabel.Text = tostring(value)
        if callback then
            callback(value)
        end
    end

    local sliding = false
    sliderBar.InputBegan:Connect(function(input)
        if input.UserInputType == Enum.UserInputType.MouseButton1 or input.UserInputType == Enum.UserInputType.Touch then
            sliding = true
            updateSlider(input.Position.X)
        end
    end)
    sliderBar.InputChanged:Connect(function(input)
        if
            input.UserInputType == Enum.UserInputType.MouseMovement
            or input.UserInputType == Enum.UserInputType.Touch
        then
            if sliding then
                updateSlider(input.Position.X)
            end
        end
    end)
    sliderBar.InputEnded:Connect(function(input)
        if input.UserInputType == Enum.UserInputType.MouseButton1 or input.UserInputType == Enum.UserInputType.Touch then
            sliding = false
        end
    end)

    self.Elements[id] = {
        ID = id,
        Type = "Slider",
        Object = frame,
        Value = sliderValue
    }
end

function Selfware:UpdateSlider(id, newVal)
    local elem = self.Elements[id]
    if elem and elem.Type == "Slider" then
        local frame = elem.Object
        local label = frame:FindFirstChildOfClass("TextLabel")
        local sliderBar = frame:FindFirstChild("Frame")
        if label and sliderBar then
            label.Text = tostring(newVal)
            -- Opt. kannst du fillBar anpassen. Müssten wir minVal/maxVal kennen
            -- -> Hier nur Label-Update
        end
        elem.Value = newVal
    end
end

-------------------------------------------
-- Element: Keybind (Create / Update)    --
-------------------------------------------
function Selfware:CreateKeybind(id, defaultKey, callback)
    local frame = Instance.new("Frame")
    frame.Size = UDim2.new(0, 200, 0, 30)
    frame.BackgroundColor3 = self.Theme.TitleBarColor
    frame.Parent = self.ContentFrame
    makeUICorner(6, frame)

    local label = Instance.new("TextLabel")
    label.Size = UDim2.new(1, 0, 1, 0)
    label.BackgroundTransparency = 1
    label.TextColor3 = self.Theme.TextColor
    label.Font = Enum.Font.SourceSans
    label.TextSize = 16
    label.Text = "Keybind: "..(defaultKey and defaultKey.Name or "None")
    label.Parent = frame

    local currentKey = defaultKey

    frame.InputBegan:Connect(function(input)
        if input.UserInputType == Enum.UserInputType.Keyboard then
            currentKey = input.KeyCode
            label.Text = "Keybind: "..currentKey.Name
            if callback then
                callback(currentKey)
            end
        end
    end)

    self.Elements[id] = {
        ID = id,
        Type = "Keybind",
        Object = frame,
        Value = defaultKey and defaultKey.Name or ""
    }
end

function Selfware:UpdateKeybind(id, newKey)
    local elem = self.Elements[id]
    if elem and elem.Type == "Keybind" then
        local label = elem.Object:FindFirstChildOfClass("TextLabel")
        if label then
            label.Text = "Keybind: "..(newKey and newKey.Name or "None")
        end
        elem.Value = newKey and newKey.Name or ""
    end
end

-------------------------------------------
-- Element: Divider (Create/Update)      --
-------------------------------------------
function Selfware:CreateDivider(id)
    local line = Instance.new("Frame")
    line.Size = UDim2.new(1, -10, 0, 2)
    line.BackgroundColor3 = self.Theme.AccentColor
    line.Parent = self.ContentFrame

    self.Elements[id] = {
        ID = id,
        Type = "Divider",
        Object = line,
        Value = ""
    }
end

function Selfware:UpdateDivider(id, newColor)
    local elem = self.Elements[id]
    if elem and elem.Type == "Divider" then
        elem.Object.BackgroundColor3 = newColor
    end
end

-------------------------------------------
-- Element: Section (Create/Update)      --
-------------------------------------------
function Selfware:CreateSection(id, sectionTitle)
    local frame = Instance.new("Frame")
    frame.Size = UDim2.new(1, -10, 0, 30)
    frame.BackgroundColor3 = self.Theme.TitleBarColor
    frame.Parent = self.ContentFrame
    makeUICorner(6, frame)

    local label = Instance.new("TextLabel")
    label.Size = UDim2.new(1, 0, 1, 0)
    label.BackgroundTransparency = 1
    label.TextColor3 = self.Theme.TextColor
    label.Font = Enum.Font.SourceSansBold
    label.TextSize = 16
    label.Text = sectionTitle
    label.Parent = frame

    self.Elements[id] = {
        ID = id,
        Type = "Section",
        Object = frame,
        Value = sectionTitle
    }
end

function Selfware:UpdateSection(id, newTitle)
    local elem = self.Elements[id]
    if elem and elem.Type == "Section" then
        local label = elem.Object:FindFirstChildOfClass("TextLabel")
        if label then
            label.Text = newTitle
        end
        elem.Value = newTitle
    end
end

--------------------------------
-- Wert eines Elements holen  --
--------------------------------
function Selfware:GetValue(id)
    local elem = self.Elements[id]
    if elem then
        return elem.Value
    end
    return nil
end

-------------------------------------
-- Interface zerstören / schließen --
-------------------------------------
function Selfware:DestroyInterface()
    if self.ScreenGui then
        self.ScreenGui:Destroy()
    end
end

------------------
-- Return Modul --
------------------
return Selfware
