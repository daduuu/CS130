import { Link } from "react-router-dom";
import React from 'react';
import { addRecipeToUser } from "../api/api";


export interface TileProps {
    index: Number,
    name: string,
    id: string,
    link: any,
    isUser: boolean
}


export function Tile({index, name, id, link, isUser}: TileProps){
    const globalUser = 'a11bbaa8-0b32-4e73-9299-a017b2018a40';

    function removeRecipeFromUser(){

    }

    return (
        <div className="flex w-full justify-center my-3">
            <div className="relative flex place-items-center w-1/2 h-20 bg-slate-200 rounded-md border-2 border-black" >
                <div className='p-5 text-lg font-bold'>{index.toString()}.</div>
                <img src={link} alt="test" className='h-full p-5'/>
                {isUser ? 
                    (<Link to={'/user/'+id + '/recipes'} className='p-5 font-bold'> {name} </Link>)
                    :
                    (<>
                        <Link to={'/recipe/'+id} className='p-5 font-bold'> {name} </Link>
                        {(globalUser == id) ? 
                            (<button onClick={removeRecipeFromUser} className="absolute border-black rounded-md right-5 m-1 w-6 h-6 hover:bg-logo-red">
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" />
                                </svg>
                            </button>) 
                            :
                            (<button onClick={() => {addRecipeToUser(globalUser, id)}} className="absolute border-black rounded-md right-5 m-1 w-6 h-6 hover:bg-logo-red">
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
                                </svg>
                            </button>)
                        }
                    </>)
                }
            </div>
        </div>
    )
}