// src/lib/api/auth.ts


import {
  apiClient
} from "./client";



export interface User {

  id: number;

  email: string;

  full_name: string | null;

}



export interface LoginResponse {

  access_token: string;

  refresh_token: string;

  token_type: string;

}



export interface RegisterRequest {

  email: string;

  password: string;

  full_name?: string;

}



// ================================
// Login
// ================================

export async function login(
  email: string,
  password: string
) {


  return apiClient<LoginResponse>(
    "/auth/login",
    {
      method: "POST",

      token: false,

      body: JSON.stringify({
        email,
        password,
      }),
    }
  );

}



// ================================
// Register
// ================================

export async function register(
  data: RegisterRequest
) {


  return apiClient<User>(
    "/auth/register",
    {
      method: "POST",

      token: false,

      body: JSON.stringify(data),
    }
  );

}



// ================================
// Current User
// ================================

export async function getCurrentUser(){

  return apiClient<User>(
    "/auth/me",
    {
      method:"GET",
    }
  );

}