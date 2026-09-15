"use client";

import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import { useRouter } from "next/navigation";



interface User {

  id: number;

  email: string;

  full_name: string | null;

}



interface RegisterData {

  full_name: string;

  email: string;

  password: string;

}



interface AuthContextType {

  user: User | null;

  token: string | null;

  loading: boolean;

  isAuthenticated: boolean;


  login(
    email: string,
    password: string
  ): Promise<void>;



  register(
    data:RegisterData
  ): Promise<void>;



  logout():void;

}



const AuthContext =
createContext<AuthContextType | undefined>(
  undefined
);



const API_URL =
process.env.NEXT_PUBLIC_API_URL ??
"http://127.0.0.1:8000/api";



const TOKEN_KEY =
"orion_access_token";


const REFRESH_KEY =
"orion_refresh_token";


const USER_KEY =
"orion_user";




export function AuthProvider({
  children,
}:{
  children:ReactNode;
}) {


  const router =
    useRouter();



  const [user,setUser] =
    useState<User | null>(null);



  const [token,setToken] =
    useState<string | null>(null);



  const [loading,setLoading] =
    useState(true);





  // =====================================
  // Restore Session
  // =====================================

  useEffect(()=>{


    async function restoreSession(){


      const storedToken =
        localStorage.getItem(
          TOKEN_KEY
        );



      if(!storedToken){

        setLoading(false);

        return;

      }



      try{


        const response =
        await fetch(
          `${API_URL}/auth/me`,
          {

            headers:{

              Authorization:
              `Bearer ${storedToken}`,

            },

          }

        );



        if(!response.ok){

          throw new Error(
            "Session expired"
          );

        }



        const currentUser =
          await response.json();



        setToken(
          storedToken
        );


        setUser(
          currentUser
        );



        localStorage.setItem(
          USER_KEY,
          JSON.stringify(
            currentUser
          )
        );



      }
      catch(error){


        logout();


      }
      finally{

        setLoading(false);

      }


    }



    restoreSession();


  },[]);







  // =====================================
  // Login
  // =====================================

  async function login(
    email:string,
    password:string
  ){


    const response =
    await fetch(
      `${API_URL}/auth/login`,
      {

        method:"POST",

        headers:{

          "Content-Type":
          "application/json",

        },


        body:JSON.stringify({

          email,

          password,

        }),

      }

    );



    const data =
      await response.json();



    if(!response.ok){

      throw new Error(
        data.detail ??
        "Login failed"
      );

    }





    const accessToken =
      data.access_token;



    const refreshToken =
      data.refresh_token;





    localStorage.setItem(
      TOKEN_KEY,
      accessToken
    );



    localStorage.setItem(
      REFRESH_KEY,
      refreshToken
    );



    setToken(
      accessToken
    );







    // Fetch current user

    const userResponse =
    await fetch(
      `${API_URL}/auth/me`,
      {

        headers:{

          Authorization:
          `Bearer ${accessToken}`,

        },

      }

    );



    const currentUser =
      await userResponse.json();




    if(!userResponse.ok){

      throw new Error(
        "Unable to load user"
      );

    }




    localStorage.setItem(
      USER_KEY,
      JSON.stringify(
        currentUser
      )
    );



    setUser(
      currentUser
    );



    console.log("Redirecting now");

    router.replace("/dashboard");


  }







  // =====================================
  // Register
  // =====================================

  async function register(
    data:RegisterData
  ){


    const response =
    await fetch(
      `${API_URL}/auth/register`,
      {

        method:"POST",

        headers:{

          "Content-Type":
          "application/json",

        },


        body:JSON.stringify(
          data
        ),

      }

    );



    const result =
      await response.json();



    if(!response.ok){

      throw new Error(
        result.detail ??
        "Registration failed"
      );

    }


  }







  // =====================================
  // Logout
  // =====================================

  function logout(){


    localStorage.removeItem(
      TOKEN_KEY
    );


    localStorage.removeItem(
      REFRESH_KEY
    );


    localStorage.removeItem(
      USER_KEY
    );



    setToken(null);


    setUser(null);



    router.push(
      "/login"
    );

  }







  const value =
  useMemo(

    ()=>({

      user,

      token,

      loading,

      isAuthenticated:
        Boolean(token),


      login,

      register,

      logout,

    }),

    [
      user,
      token,
      loading
    ]

  );





  return (

    <AuthContext.Provider
      value={value}
    >

      {children}

    </AuthContext.Provider>

  );


}






export function useAuth(){


  const context =
    useContext(
      AuthContext
    );



  if(!context){

    throw new Error(
      "useAuth must be used inside AuthProvider"
    );

  }



  return context;


}