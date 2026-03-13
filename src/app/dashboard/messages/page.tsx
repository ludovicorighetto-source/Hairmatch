"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { Loader2, Send, MessageSquare, ChevronLeft } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  apiListConversations,
  apiGetMessages,
  apiSendMessage,
  apiMarkAsRead,
  type ConversationResponse,
  type MessageResponse,
} from "@/lib/api/messages";

function formatTime(iso: string) {
  const d = new Date(iso);
  const now = new Date();
  const isToday = d.toDateString() === now.toDateString();
  if (isToday) {
    return d.toLocaleTimeString("it-IT", { hour: "2-digit", minute: "2-digit" });
  }
  return d.toLocaleDateString("it-IT", { day: "2-digit", month: "short" });
}

function shortId(uuid: string) {
  return uuid.slice(0, 8);
}

export default function MessagesPage() {
  const { user, accessToken } = useAuth();

  const [conversations, setConversations] = useState<ConversationResponse[]>([]);
  const [loadingConvs, setLoadingConvs] = useState(true);
  const [selectedConv, setSelectedConv] = useState<ConversationResponse | null>(null);
  const [messages, setMessages] = useState<MessageResponse[]>([]);
  const [loadingMsgs, setLoadingMsgs] = useState(false);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  const loadConversations = useCallback(async () => {
    if (!accessToken) return;
    try {
      const convs = await apiListConversations(accessToken);
      setConversations(convs);
    } catch {
      // silent
    } finally {
      setLoadingConvs(false);
    }
  }, [accessToken]);

  const openConversation = useCallback(
    async (conv: ConversationResponse) => {
      if (!accessToken) return;
      setSelectedConv(conv);
      setLoadingMsgs(true);
      try {
        const msgs = await apiGetMessages(accessToken, conv.id);
        setMessages(msgs);
        if (conv.unread_count > 0) {
          await apiMarkAsRead(accessToken, conv.id);
          setConversations((prev) =>
            prev.map((c) => (c.id === conv.id ? { ...c, unread_count: 0 } : c))
          );
        }
      } catch {
        // silent
      } finally {
        setLoadingMsgs(false);
      }
    },
    [accessToken]
  );

  useEffect(() => {
    loadConversations();
  }, [loadConversations]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!accessToken || !selectedConv || !input.trim()) return;
    setSending(true);
    try {
      const msg = await apiSendMessage(accessToken, selectedConv.id, input.trim());
      setMessages((prev) => [...prev, msg]);
      setInput("");
      // Update conversation preview
      setConversations((prev) =>
        prev.map((c) =>
          c.id === selectedConv.id ? { ...c, last_message: msg, updated_at: msg.created_at } : c
        )
      );
    } catch {
      // silent
    } finally {
      setSending(false);
    }
  };

  if (!user) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
      </div>
    );
  }

  const totalUnread = conversations.reduce((s, c) => s + c.unread_count, 0);

  return (
    <div className="flex h-[calc(100vh-8rem)] gap-4">
      {/* Sidebar — conversation list */}
      <div
        className={`flex w-full flex-col md:w-72 lg:w-80 ${
          selectedConv ? "hidden md:flex" : "flex"
        }`}
      >
        <div className="mb-3 flex items-center justify-between">
          <h1 className="text-xl font-bold text-gray-900">
            Messaggi
            {totalUnread > 0 && (
              <span className="ml-2 rounded-full bg-indigo-600 px-2 py-0.5 text-xs text-white">
                {totalUnread}
              </span>
            )}
          </h1>
        </div>

        {loadingConvs ? (
          <div className="flex flex-1 items-center justify-center">
            <Loader2 className="h-6 w-6 animate-spin text-indigo-500" />
          </div>
        ) : conversations.length === 0 ? (
          <Card className="flex-1 border-dashed">
            <CardContent className="flex flex-col items-center justify-center py-12 text-center">
              <MessageSquare className="mb-3 h-10 w-10 text-gray-300" />
              <p className="text-sm text-gray-500">
                Nessuna conversazione ancora.
              </p>
              <p className="mt-1 text-xs text-gray-400">
                Avvia una chat dal profilo di un professionista o salone.
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="flex-1 overflow-y-auto space-y-1">
            {conversations.map((conv) => (
              <button
                key={conv.id}
                onClick={() => openConversation(conv)}
                className={`w-full rounded-lg p-3 text-left transition-colors ${
                  selectedConv?.id === conv.id
                    ? "bg-indigo-50 border border-indigo-200"
                    : "hover:bg-gray-50 border border-transparent"
                }`}
              >
                {/* Avatar */}
                <div className="flex items-start gap-3">
                  <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-gray-200 text-xs font-bold text-gray-600">
                    {shortId(conv.other_user_id).toUpperCase().slice(0, 2)}
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-gray-900 truncate">
                        Utente {shortId(conv.other_user_id)}
                      </span>
                      <span className="text-xs text-gray-400 shrink-0 ml-2">
                        {conv.last_message
                          ? formatTime(conv.last_message.created_at)
                          : formatTime(conv.created_at)}
                      </span>
                    </div>
                    <p className="truncate text-xs text-gray-500 mt-0.5">
                      {conv.last_message?.content ?? "Inizia a scrivere..."}
                    </p>
                  </div>
                  {conv.unread_count > 0 && (
                    <span className="ml-1 flex h-5 w-5 items-center justify-center rounded-full bg-indigo-600 text-xs font-bold text-white">
                      {conv.unread_count}
                    </span>
                  )}
                </div>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Chat area */}
      <div
        className={`flex flex-1 flex-col ${
          selectedConv ? "flex" : "hidden md:flex"
        }`}
      >
        {!selectedConv ? (
          <Card className="flex flex-1 items-center justify-center border-dashed">
            <CardContent className="text-center py-12">
              <MessageSquare className="mx-auto mb-3 h-12 w-12 text-gray-200" />
              <p className="text-gray-500">
                Seleziona una conversazione per iniziare
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="flex flex-1 flex-col overflow-hidden rounded-lg border bg-white">
            {/* Chat header */}
            <div className="flex items-center gap-3 border-b px-4 py-3">
              <button
                className="md:hidden text-gray-500 hover:text-gray-700"
                onClick={() => setSelectedConv(null)}
              >
                <ChevronLeft className="h-5 w-5" />
              </button>
              <div className="flex h-9 w-9 items-center justify-center rounded-full bg-gray-200 text-xs font-bold text-gray-600">
                {shortId(selectedConv.other_user_id).toUpperCase().slice(0, 2)}
              </div>
              <div>
                <p className="font-medium text-gray-900 text-sm">
                  Utente {shortId(selectedConv.other_user_id)}
                </p>
                <p className="text-xs text-gray-400">
                  ID: {selectedConv.other_user_id.slice(0, 12)}…
                </p>
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-3">
              {loadingMsgs ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="h-6 w-6 animate-spin text-indigo-500" />
                </div>
              ) : messages.length === 0 ? (
                <p className="text-center text-sm text-gray-400">
                  Nessun messaggio ancora. Scrivi per iniziare!
                </p>
              ) : (
                messages.map((msg) => {
                  const isMine = msg.sender_id === user.id;
                  return (
                    <div
                      key={msg.id}
                      className={`flex ${isMine ? "justify-end" : "justify-start"}`}
                    >
                      <div
                        className={`max-w-[70%] rounded-2xl px-4 py-2 text-sm ${
                          isMine
                            ? "bg-indigo-600 text-white rounded-br-none"
                            : "bg-gray-100 text-gray-900 rounded-bl-none"
                        }`}
                      >
                        <p>{msg.content}</p>
                        <p
                          className={`mt-0.5 text-right text-[10px] ${
                            isMine ? "text-indigo-200" : "text-gray-400"
                          }`}
                        >
                          {formatTime(msg.created_at)}
                          {isMine && (
                            <span className="ml-1">
                              {msg.is_read ? "✓✓" : "✓"}
                            </span>
                          )}
                        </p>
                      </div>
                    </div>
                  );
                })
              )}
              <div ref={bottomRef} />
            </div>

            {/* Input */}
            <form
              onSubmit={handleSend}
              className="flex items-center gap-2 border-t px-4 py-3"
            >
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Scrivi un messaggio…"
                className="flex-1 rounded-full border border-gray-300 px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                disabled={sending}
              />
              <Button
                type="submit"
                size="sm"
                disabled={sending || !input.trim()}
                className="rounded-full bg-indigo-600 hover:bg-indigo-700 h-9 w-9 p-0"
              >
                {sending ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Send className="h-4 w-4" />
                )}
              </Button>
            </form>
          </div>
        )}
      </div>
    </div>
  );
}
