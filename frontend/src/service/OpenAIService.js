import { sendLibraryAssistantMessage } from "@/features/material/api/materialApi";

export async function sendOpenAIChat(prompt, history = []) {
  const response = await sendLibraryAssistantMessage({
    prompt,
    history,
  });

  if (!response?.success) {
    throw new Error(response?.error || "Failed to get response from the AI service.");
  }

  return (
    response?.data?.message?.trim() ||
    "I am sorry, I could not generate an answer right now."
  );
}
