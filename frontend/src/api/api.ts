import axios from "axios";
import { SingleObject } from "../components/tileList";

export const api = axios.create({
    baseURL: "http://127.0.0.1:5000/api",
});

export async function getRecipes(userId: string) : Promise<SingleObject[]>{
    const response = await api.get<{ message: string }>(
        "/user_info", 
        {params: {"user_id": userId}}
    )
    console.log(response)
    return [];
}

export async function searchRecipes(searchText: (string|null)) : Promise<SingleObject[]>{
    return [];
}


export async function uploadImage(file: File): Promise<string> {
    const formData = new FormData();
    formData.append("file", file);

    const response = await api.post<{ message: string }>("/upload", formData, {
        headers: {
            "Content-Type": "multipart/form-data",
        },
    });

    if (response.status !== 200) {
        throw new Error(response.data.message);
    }

    return response.data.message;
}

export async function signUp(
    email: string,
    userName: string,
    password: string
): Promise<{
    email: string;
    username: string;
}> {
    const response = await api
        .post<{ message: string }>(
            "/signup",
            JSON.stringify({
                email,
                userName,
                password,
            }),
            {
                headers: {
                    "Content-Type": "application/json",
                },
            }
        )
        .catch((error) => {
            console.log(error);
            return error.response.data;
        });

    if (response.error) {
        throw new Error(response.error);
    }

    return {
        email: response.data.email,
        username: response.data.username,
    };
}

export async function signIn(
    email: string,
    password: string
): Promise<{
    email: string;
    username: string;
}> {
    const response = await api
        .post<{ email: string; username: string; error: string }>(
            "/login",
            JSON.stringify({
                email,
                password,
            }),
            {
                headers: {
                    "Content-Type": "application/json",
                },
            }
        )
        .catch((error) => {
            return error.response.data;
        });

    if (response.error) {
        console.log(response.error);
        throw new Error(response.error);
    }

    return {
        email: response.data.email,
        username: response.data.username,
    };
}
