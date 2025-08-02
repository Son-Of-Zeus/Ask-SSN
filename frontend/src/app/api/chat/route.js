export async function POST(req) {
  const body = await req.json();
  console.log("Request Body:", body);

    const res = await fetch('http://127.0.0.1:8000/api/chat_completion/', {
    method: 'POST',
        headers: { 'Content-Type': 'application/json' },
    body,
    // body: JSON.stringify(
    //   {
    //     "query: [
    //       {
    //         "content": "Hey There !",
    //         "role": "user"
    //       },
    //       {
    //         "content": "Hello ! I am a humble chat bot",
    //         "role": "assistant"
    //       },
    //       {
    //         "content": "Who are you again ?",
    //         "role": "user"
    //       }
    //     ]
    //   }
    // ),
    body: JSON.stringify(body)
  });
  const data = await res.json();
  return Response.json(data);
}