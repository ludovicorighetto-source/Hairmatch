export type SubscriptionPlan = "free" | "basic" | "premium" | "enterprise";
export type AvailabilityStatus =
  | "available"
  | "partially_available"
  | "not_available"
  | "on_leave";

export interface OpeningHoursDay {
  open: string;
  close: string;
  closed: boolean;
}

export type OpeningHours = Record<string, OpeningHoursDay | null>;

// ── Salon ──────────────────────────────────────────────────────────────────────

export interface SalonProfile {
  id: string;
  user_id: string;
  business_name: string;
  phone: string;
  address_street: string;
  address_city: string;
  address_province: string;
  address_postal_code: string;
  address_country: string;
  vat_number: string | null;
  website_url: string | null;
  description: string | null;
  seats_count: number | null;
  opening_hours: OpeningHours | null;
  logo_url: string | null;
  cover_image_url: string | null;
  latitude: number | null;
  longitude: number | null;
  subscription_plan: SubscriptionPlan;
  subscription_expires_at: string | null;
  is_profile_complete: boolean;
  is_featured: boolean;
  created_at: string;
  updated_at: string;
}

export interface UpdateSalonProfileRequest {
  business_name?: string;
  phone?: string;
  description?: string;
  website_url?: string;
  vat_number?: string;
  address_street?: string;
  address_city?: string;
  address_province?: string;
  address_postal_code?: string;
  seats_count?: number;
  opening_hours?: OpeningHours;
  latitude?: number;
  longitude?: number;
  logo_url?: string;
  cover_image_url?: string;
}

// ── Professional ───────────────────────────────────────────────────────────────

export interface ProfessionalProfile {
  id: string;
  user_id: string;
  first_name: string;
  last_name: string;
  phone: string;
  date_of_birth: string | null;
  bio: string | null;
  specializations: string[];
  years_of_experience: number | null;
  preferred_city: string | null;
  preferred_province: string | null;
  max_travel_km: number;
  is_available_remotely: boolean;
  preferred_contract_types: string[];
  availability_status: AvailabilityStatus;
  profile_photo_url: string | null;
  portfolio_urls: string[];
  subscription_plan: SubscriptionPlan;
  subscription_expires_at: string | null;
  is_profile_complete: boolean;
  is_featured: boolean;
  created_at: string;
  updated_at: string;
}

export interface UpdateProfessionalProfileRequest {
  first_name?: string;
  last_name?: string;
  phone?: string;
  date_of_birth?: string;
  bio?: string;
  specializations?: string[];
  years_of_experience?: number;
  preferred_city?: string;
  preferred_province?: string;
  max_travel_km?: number;
  is_available_remotely?: boolean;
  preferred_contract_types?: string[];
  availability_status?: AvailabilityStatus;
  profile_photo_url?: string;
  portfolio_urls?: string[];
}

// ── Public profile ─────────────────────────────────────────────────────────────

export interface PublicUser {
  id: string;
  role: "salon" | "professional";
  is_verified: boolean;
  created_at: string;
}

export interface PublicSalonProfile {
  user: PublicUser;
  profile: SalonProfile;
}

export interface PublicProfessionalProfile {
  user: PublicUser;
  profile: ProfessionalProfile;
}

export type PublicProfile = PublicSalonProfile | PublicProfessionalProfile;
