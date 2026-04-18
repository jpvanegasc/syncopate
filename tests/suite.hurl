GET http://localhost:8888/async/get
HTTP 200
[Asserts]
body == "/async/get"


POST http://localhost:8888/async/post
Content-Type: application/json
{"async":"post"}
HTTP 200
[Asserts]
body == "{\"async\": \"post\"}"
