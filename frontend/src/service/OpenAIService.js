export async function sendOpenAIChat(prompt, history = []) {

  const apiKey = import.meta.env.VITE_OPENAI_API_KEY || import.meta.env.v_OPENAI_API_KEY ||VITE_OPENAI_API_KEY;
  if (!apiKey) {
    throw new Error(
      'OpenAI API key is not configured. Set VITE_OPENAI_API_KEY in your environment.'
    );
  }

  const systemMessage = {
    role: 'system',
    content:
      'You are a helpful virtual assistant for a university library system. Answer user questions clearly and politely, focusing on library policies, book loans, returns, fines, and general library services.',
  };

  const messages = [
    systemMessage,
    ...history,
    { role: 'user', content: prompt },
  ];

  const response = await fetch('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${apiKey}`,
    },
    body: JSON.stringify({
      model: 'gpt-3.5-turbo',
      messages,
      temperature: 0.4,
      max_tokens: 400,
    }),
  });

  const result = await response.json();

  if (!response.ok) {
    const errorMessage = result.error?.message || 'Failed to get response from OpenAI.';
    throw new Error(errorMessage);
  }

  return result.choices?.[0]?.message?.content?.trim() || 'I am sorry, I could not generate an answer right now.';
}
