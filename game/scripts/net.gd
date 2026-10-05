extends Node
## Bağlantı katmanı. `--server` argümanı ile headless sunucu, aksi halde istemci.
const DEFAULT_PORT := 9080
var is_server := false

func _ready() -> void:
	var args := OS.get_cmdline_user_args()
	if "--server" in args:
		var port := DEFAULT_PORT
		var i := args.find("--port")
		if i >= 0 and i + 1 < args.size(): port = int(args[i + 1])
		start_server(port)

func start_server(port: int) -> void:
	is_server = true
	var peer := WebSocketMultiplayerPeer.new()
	var err := peer.create_server(port)
	assert(err == OK, "sunucu açılamadı: %s" % err)
	multiplayer.multiplayer_peer = peer
	print("3-2-1 sunucu dinliyor :%d" % port)

func connect_to(url: String) -> Error:
	var peer := WebSocketMultiplayerPeer.new()
	var err := peer.create_client(url)
	if err == OK: multiplayer.multiplayer_peer = peer
	return err
