export type UserRole = "salon" | "professional";

export interface AuthUser {
  id: string;
  email: string;
  role: UserRole;
  business_name?: string; // salon
  first_name?: string;    // professional
  last_name?: string;     // professional
  is_verified: boolean;
  is_active: boolean;
}

export interface AuthState {
  user: AuthUser | null;
  accessToken: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<void>;
  setUser: (user: AuthUser | null, accessToken: string | null) => void;
}

// API request/response shapes

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: AuthUser;
}

export interface SalonRegisterRequest {
  email: string;
  password: string;
  business_name: string;
  phone: string;
  address: {
    street: string;
    city: string;
    province: string;
    postal_code: string;
  };
  vat_number?: string;
  website?: string;
}

export interface ProfessionalRegisterRequest {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  phone: string;
  specializations: string[];
  years_of_experience?: number;
  preferred_city?: string;
  preferred_province?: string;
}

export interface RegisterResponse {
  message: string;
  user_id: string;
}

export interface RefreshResponse {
  access_token: string;
  token_type: string;
}

// API Error shapes
export interface ApiError {
  detail: string | ApiFieldError[];
  status_code?: number;
}

export interface ApiFieldError {
  loc: string[];
  msg: string;
  type: string;
}

// JWT payload
export interface JWTPayload {
  sub: string;
  email: string;
  role: UserRole;
  exp: number;
  iat: number;
}

// Specializations
export const SPECIALIZATIONS = [
  "Taglio",
  "Colorazione",
  "Extension",
  "Permanente",
  "Trattamenti",
  "Barbiere",
  "Acconciatura sposa",
  "Nail art",
] as const;

export type Specialization = typeof SPECIALIZATIONS[number];

// Italian provinces
export const ITALIAN_PROVINCES = [
  "AG", "AL", "AN", "AO", "AP", "AQ", "AR", "AT", "AV",
  "BA", "BG", "BI", "BL", "BN", "BO", "BR", "BS", "BT", "BZ",
  "CA", "CB", "CE", "CH", "CL", "CN", "CO", "CR", "CS", "CT", "CZ",
  "EN",
  "FC", "FE", "FG", "FI", "FM", "FR",
  "GE", "GO", "GR",
  "IM", "IS",
  "KR",
  "LC", "LE", "LI", "LO", "LT", "LU",
  "MB", "MC", "ME", "MI", "MN", "MO", "MS", "MT",
  "NA", "NO", "NU",
  "OR",
  "PA", "PC", "PD", "PE", "PG", "PI", "PN", "PO", "PR", "PT", "PU", "PV", "PZ",
  "RA", "RC", "RE", "RG", "RI", "RM", "RN", "RO",
  "SA", "SI", "SO", "SP", "SR", "SS", "SU", "SV",
  "TA", "TE", "TN", "TO", "TP", "TR", "TS", "TV",
  "UD",
  "VA", "VB", "VC", "VE", "VI", "VR", "VT", "VV",
] as const;
