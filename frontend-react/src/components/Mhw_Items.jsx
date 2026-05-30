import React from 'react'
// import { Link } from 'react-router-dom'
import { useNavigate } from "react-router-dom";

function Mhw_Items({manhwa}) {
    const navigate = useNavigate();
  return (
    // <Link>
     <div onClick={() => navigate(`/manhwa/details/${manhwa.slug}`)} key={manhwa.slug} alt="Manhwa" className="flex flex-col h-max-fit gap-2 bg-zinc-800/70 w-1/5   backdrop-blur-lg rounded-2xl border border-zinc-800 shadow-2xl p-4">
       <div className='overflow-hidden w-full h-[360px] rounded-2xl '>
        {/* <Image ></Image> */}
        <img className='w-full h-[350px] content-center overflow-hidden '  src={manhwa.poster_url} alt="Poster"  />
        </div> 
       
       <div className='overflow-hidden'>
        <h3 className="text-lg font-mono text-nowrap font-semibold underline mb-2">{manhwa.title.length > 25 ? manhwa.title.slice(0, 20) + '...' : manhwa.title}</h3>
        <div className="bg-white rounded-3xl w-fit h-fit p-1 text-black py-0 px-2">Chapters : {manhwa.number_of_chapters}</div>

      </div> 
      {/* </Link> */}
    </div>
  )
}

export default Mhw_Items