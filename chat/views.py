import os
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from groq import Groq


@login_required
def chat_home(request):
    return render(request, "chat/chat.html")


@login_required
def send_message(request):
    if request.method != "POST":
        return JsonResponse({"reply": "Invalid request"})

    user_message = request.POST.get("message", "").strip()
    if not user_message:
        return JsonResponse({"reply": "Please type a message"})

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return JsonResponse({"reply": "❌ GROQ_API_KEY not loaded"})

    try:
        client = Groq(api_key=api_key)
        
        # Get user's name for personalization
        user_name = request.user.first_name if request.user.first_name else request.user.username

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",  # ✅ VALID FREE MODEL
            messages=[
                {
                    "role": "system",
                    "content": f"You are FinanceAI, a helpful personal finance assistant. You are currently talking to {user_name}. Always be professional and friendly. If they say hi or hello, greet them by their name: {user_name}."
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            temperature=0.6,
            max_tokens=300
        )

        return JsonResponse({
            "reply": response.choices[0].message.content
        })

    except Exception as e:
        print("🔥 GROQ ERROR:", e)
        return JsonResponse({
            "reply": "⚠️ AI service error. See server logs."
        })
