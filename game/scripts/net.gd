extends Node
## Bağlantı katmanı. `--server` ile headless sunucu; aksi halde istemci.
const DEFAULT_PORT := 9080
signal connected
signal disconnected
signal connect_failed

var is_server := false
var server_url := "ws://127.0.0.1:9080"

func _ready() -> void:
	var args := OS.get_cmdline_user_args()
	if "--server" in args:
		var port := DEFAULT_PORT
		var i := args.find("--port")
		if i >= 0 and i + 1 < args.size(): port = int(args[i + 1])
		start_server(port)
	else:
		if OS.has_feature("web"):
			var host: String = JavaScriptBridge.eval("location.hostname") if OS.has_feature("web") else "127.0.0.1"
			var https: bool = JavaScriptBridge.eval("location.protocol") == "https:"
			server_url = ("wss://%s/ws" % host) if https else ("ws://%s:%d" % [host, DEFAULT_PORT])
		var i := args.find("--connect")
		if i >= 0 and i + 1 < args.size(): server_url = args[i + 1]

func start_server(port: int) -> void:
	is_server = true
	var peer := WebSocketMultiplayerPeer.new()
	var err := peer.create_server(port)
	assert(err == OK, "sunucu açılamadı: %s" % err)
	multiplayer.multiplayer_peer = peer
	print("3-2-1 Kickoff sunucu :%d" % port)

func connect_to_server() -> void:
	if multiplayer.multiplayer_peer is WebSocketMultiplayerPeer and multiplayer.multiplayer_peer.get_connection_status() != MultiplayerPeer.CONNECTION_DISCONNECTED:
		return
	var peer := WebSocketMultiplayerPeer.new()
	var err := peer.create_client(server_url)
	print("[net] create_client ", server_url, " → ", err)
	if err != OK:
		connect_failed.emit(); return
	multiplayer.multiplayer_peer = peer
	if not multiplayer.connected_to_server.is_connected(_on_connected):
		multiplayer.connected_to_server.connect(_on_connected)
		multiplayer.connection_failed.connect(func(): connect_failed.emit())
		multiplayer.server_disconnected.connect(func(): disconnected.emit())

func _on_connected() -> void:
	connected.emit()

func is_connected_to_server() -> bool:
	var p := multiplayer.multiplayer_peer
	return p is WebSocketMultiplayerPeer and p.get_connection_status() == MultiplayerPeer.CONNECTION_CONNECTED and not is_server
