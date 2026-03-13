import type { JobStatus } from "@/types/jobs";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const BASE = `${API_BASE_URL}/api/v1/messages`;

async function msgFetch<T>(
  path: string,
  token: string,
  options: RequestInit = {}
): Promise<T> {
  const resp = await fetch(`${BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...(options.headers || {}),
    },
  });
  if (!resp.ok) {
    const detail = await resp.json().catch(() => ({ detail: resp.statusText }));
    throw new Error(detail?.detail || `HTTP ${resp.status}`);
  }
  if (resp.status === 204) return undefined as T;
  return resp.json() as Promise<T>;
}

export interface MessageResponse {
  id: string;
  conversation_id: string;
  sender_id: string;
  content: string;
  is_read: boolean;
  created_at: string;
}

export interface ConversationResponse {
  id: string;
  participant_a_id: string;
  participant_b_id: string;
  created_at: string;
  updated_at: string;
  other_user_id: string;
  unread_count: number;
  last_message: MessageResponse | null;
}

export async function apiStartConversation(
  token: string,
  otherUserId: string,
  initialMessage?: string
): Promise<ConversationResponse> {
  return msgFetch("/conversations", token, {
    method: "POST",
    body: JSON.stringify({
      other_user_id: otherUserId,
      initial_message: initialMessage ?? null,
    }),
  });
}

export async function apiListConversations(
  token: string
): Promise<ConversationResponse[]> {
  return msgFetch("/conversations", token, { cache: "no-store" });
}

export async function apiGetMessages(
  token: string,
  conversationId: string,
  limit = 50
): Promise<MessageResponse[]> {
  return msgFetch(
    `/conversations/${conversationId}/messages?limit=${limit}`,
    token,
    { cache: "no-store" }
  );
}

export async function apiSendMessage(
  token: string,
  conversationId: string,
  content: string
): Promise<MessageResponse> {
  return msgFetch(`/conversations/${conversationId}/messages`, token, {
    method: "POST",
    body: JSON.stringify({ content }),
  });
}

export async function apiMarkAsRead(
  token: string,
  conversationId: string
): Promise<{ marked_read: number }> {
  return msgFetch(`/conversations/${conversationId}/read`, token, {
    method: "PATCH",
  });
}
