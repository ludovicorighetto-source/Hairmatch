export type AvailabilityStatus =
  | "available"
  | "partially_available"
  | "not_available"
  | "on_leave";

export type SubscriptionPlan = "free" | "basic" | "premium" | "enterprise";

export interface ProfessionalCard {
  user_id: string;
  first_name: string;
  last_name: string;
  specializations: string[];
  years_of_experience: number | null;
  availability_status: AvailabilityStatus;
  preferred_city: string | null;
  preferred_province: string | null;
  bio: string | null;
  profile_photo_url: string | null;
  is_featured: boolean;
  is_profile_complete: boolean;
  subscription_plan: SubscriptionPlan;
  distance_km: number | null;
}

export interface SalonCard {
  user_id: string;
  business_name: string;
  address_city: string;
  address_province: string;
  description: string | null;
  logo_url: string | null;
  seats_count: number | null;
  is_featured: boolean;
  is_profile_complete: boolean;
  subscription_plan: SubscriptionPlan;
  distance_km: number | null;
}

export interface PaginatedResult<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

export const AVAILABILITY_LABELS: Record<AvailabilityStatus, string> = {
  available: "Disponibile subito",
  partially_available: "Parzialmente disponibile",
  not_available: "Non disponibile",
  on_leave: "In pausa",
};

export const AVAILABILITY_COLORS: Record<AvailabilityStatus, string> = {
  available: "bg-green-100 text-green-700",
  partially_available: "bg-yellow-100 text-yellow-700",
  not_available: "bg-red-100 text-red-700",
  on_leave: "bg-gray-100 text-gray-600",
};
