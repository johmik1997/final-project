import { sendLibraryAssistantMessage } from "@/features/material/api/materialApi";
import { activeLocale } from "@/i18n";

export async function sendOpenAIChat(prompt, history = []) {
  const response = await sendLibraryAssistantMessage({
    prompt,
    history,
    language: activeLocale.value || "en",
  });

  if (!response?.success) {
    throw new Error(response?.error || "Failed to get response from the AI service.");
  }

  return (
    response?.data?.message?.trim() ||
    "I am sorry, I could not generate an answer right now."
  );
}
