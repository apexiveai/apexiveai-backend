const API_URL =

  process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export type PaymentMethod =

  | "card"

  | "kbzpay"

  | "cbpay"

  | "ayapay"

  | "mpu";

export type CreatePaymentResponse = {

  id: number;

  tenant_id: number;

  plan_id: number;

  subscription_id: number | null;

  provider: string;

  payment_method: string;

  status: string;

  amount: string;

  currency: string;

  checkout_reference: string | null;

  external_payment_id: string | null;

  failure_reason: string | null;

  paid_at: string | null;

  created_at: string;

};

async function apiRequest<T>(

  path: string,

  options: RequestInit = {},

): Promise<T> {

  const token =

    typeof window !== "undefined"

      ? localStorage.getItem("apexive_token")

      : null;

  const headers = new Headers(options.headers);

  headers.set("Content-Type", "application/json");

  if (token) {

    headers.set("Authorization", `Bearer ${token}`);

  }

  const response = await fetch(`${API_URL}${path}`, {

    ...options,

    headers,

  });

  if (!response.ok) {

    let message = "Payment request failed";

    try {

      const data = await response.json();

      if (typeof data?.detail === "string") {

        message = data.detail;

      }

    } catch {}

    throw new Error(message);

  }

  return response.json();

}

export function createPayment(

  planId: number,

  paymentMethod: PaymentMethod,

) {

  return apiRequest<CreatePaymentResponse>(

    "/api/payments/create",

    {

      method: "POST",

      body: JSON.stringify({

        plan_id: planId,

        payment_method: paymentMethod,

      }),

    },

  );

}

export function getPayment(paymentId: number) {

  return apiRequest<CreatePaymentResponse>(

    `/api/payments/${paymentId}`,

  );

}