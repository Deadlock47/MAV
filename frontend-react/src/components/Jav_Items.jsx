import axios from 'axios';
import React from 'react'
import { useNavigate } from 'react-router-dom';
function Jav_Items({dvd_id,title,poster_url}) {
    const navigate = useNavigate();


  return (
    <div onClick={()=> {
        navigate('/jav/'+dvd_id);
    }} className="w-[23%] h-fit rounded-xl overflow-hidden text-white bg-gradient-to-r from-zinc-900 to-stone-800 ">
        <div className="w-auto h-auto overflow-hidden relative">
            
            <img className='w-full h-full object-cover  ' src={poster_url} alt="Poster"  />
            
            {/* Overlay */}
            <div className='absolute inset-0 bg-[#00000050]  opacity-100  flex items-end justify-center p-4'>
                <p className='text-white text-center font-semibold text-sm'>{" "}</p>
            </div>
          
        </div>
        <div className='flex pb-2   items-center gap-2 p-3'>
         
            <h3 className="text-sm display-linebreak font-semibold  mb-0">
                   <span className="bg-white rounded-3xl  w-fit h-fit p-1 text-black py-0 px-2">{dvd_id}</span>
               {" "} {title?.length > 95 ? title?.slice(0, 70) + '...' : title}</h3>
        </div>
    </div>
  )
}

export default Jav_Items