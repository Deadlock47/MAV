import { useState } from 'react'
import SearchBar from '../components/SearchBar'
import { NavLink } from 'react-router-dom'

function JAVPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [searchBy, setSearchBy] = useState('Code')
  const [showCodes, setShowCodes] = useState(false)
  const features = [
    { icon: '🎥', title: 'Video Library', desc: 'Browse extensive video collection with advanced filters' },
    { icon: '❤️', title: 'Watchlist', desc: 'Save your favorite videos for quick access' },
    { icon: '📊', title: 'Statistics', desc: 'Track your viewing history and preferences' },
    { icon: '🔍', title: 'Search & Filter', desc: 'Find exactly what you\'re looking for instantly' },
  ]

  return (
     <div className="space-y-6 pb-8">
         <div className="flex w-full gap-4 p-2 pl-4 pr-4 items-center justify-center bg-zinc-900/70 backdrop-blur-lg rounded-2xl border border-zinc-800 shadow-2xl">
          <NavLink
            to="/manhwa"
            className={({ isActive }) =>
              `px-6 py-2 m-2 rounded-xl w-full text-center font-medium transition-all duration-300 ${
                isActive
                  ? 'bg-zinc-100 text-black shadow-lg scale-105'
                  : 'bg-zinc-800 text-zinc-300 hover:bg-zinc-700 hover:text-white'
              }`
            }
          >
            Manhwa
          </NavLink>

          <NavLink
            to="/jav"
            className={({ isActive }) =>
              `px-6 py-2 m-2 rounded-xl w-full text-center font-medium transition-all duration-300 ${
                isActive
                  ? 'bg-zinc-100 text-black shadow-lg scale-105'
                  : 'bg-zinc-800 text-zinc-300 hover:bg-zinc-700 hover:text-white'
              }`
            }
          >
            JAV
          </NavLink>
        </div>
      
      {/* Hero Section */}

      <div className="glassmorphism dark:glassmorphism-dark p-2 md:p-2">
        <div className="flex flex-row items-center justify-center">
          <div className="text-3xl text-nowrap pr-3 md:text-3xl font-bold mb-4 gradient-text dark:gradient-text-dark">
            JAV Library 
          </div>
          
          <div className="flex items-center gap-3 w-full  px-4 py-3 rounded-[24px] bg-slate-950/10 dark:bg-slate-200/10 border h-16 border-white/10">
            <select
              value={searchBy}
              onChange={(event) => setSearchBy(event.target.value)}
              className="h-10 rounded-xl  border border-white/10 bg-slate-900/80 px-3 text-sm font-medium text-white outline-none transition-colors hover:bg-slate-800 focus:border-purple-500"
            >
              <option value="Code">Code</option>
              <option value="Actress">Actress</option>
              <option value="Tag">Tag</option>
            </select>
            <input
              id="search-input"
              type="search"
              value={searchQuery}
              onChange={(event) => setSearchQuery(event.target.value)}
              placeholder={"Search Items..... (ID , Actress , Tags)"}
              className="min-w-0 w-full bg-transparent outline-none text-slate-900 dark:text-slate-100 placeholder:text-slate-400 dark:placeholder:text-slate-500"
            />
            <button
              type="submit"
              className="inline-flex items-center justify-center rounded-2xl bg-linear-to-r from-dark-blue-600 to-purple-600 px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-dark-blue-600/30 transition-all duration-200 hover:brightness-110"
            >
              Search
            </button>
          </div>

        </div>
        {/* Content Page  */}
       

        <div className="flex flex-row justify-between mt-4">
          <div className="text-3xl text-nowrap  bg-purple-800 outline-amber-50 outline-1 rounded-2xl  md:text-2xl px-4 py-1 font-bold mb-4 gradient-text dark:gradient-text-dark">
            Filter
          </div>
          <div className='w-fit h-fit gap-2 flex flex-row'>
            <label className="flex items-center gap-3 rounded-md p-2 text-white">
              <input
                type="checkbox"
                checked={showCodes}
                onChange={(event) => setShowCodes(event.target.checked)}
                className="peer sr-only"
              />
              <span className="relative h-6 w-11 rounded-full bg-zinc-700 transition-colors duration-200 peer-checked:bg-purple-500 after:absolute after:left-1 after:top-1 after:h-4 after:w-4 after:rounded-full after:bg-white after:transition-transform after:duration-200 peer-checked:after:translate-x-5"></span>
              All Codes
            </label>
          </div>
        </div>
        {showCodes && (
          <div className="rounded-md bg-zinc-900/80 p-4 text-white outline-1 outline-white/20">
            Your codes will show here.
          </div>
        )}
      </div>
    </div>
  )
}

export default JAVPage
