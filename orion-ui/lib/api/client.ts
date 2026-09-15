// src/lib/api/client.ts

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  "http://127.0.0.1:8000/api";



interface RequestOptions
  extends RequestInit {
  token?: boolean;
}



export async function apiClient<T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {


  const {
    token = true,
    ...fetchOptions
  } = options;



  const headers = new Headers(
    fetchOptions.headers
  );


  headers.set(
    "Content-Type",
    "application/json"
  );



  if (token) {

    const accessToken =
      typeof window !== "undefined"
        ? localStorage.getItem(
            "access_token"
          )
        : null;



    if (accessToken) {

      headers.set(
        "Authorization",
        `Bearer ${accessToken}`
      );

    }

  }



  const response =
    await fetch(
      `${API_URL}${endpoint}`,
      {
        ...fetchOptions,
        headers,
      }
    );



  const data =
    await response.json();



  if (!response.ok) {

    throw new Error(
      data.detail ||
      "Something went wrong"
    );

  }



  return data;

}