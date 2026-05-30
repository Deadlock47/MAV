import { useState } from 'react'

function SearchBar({ label = 'Search', placeholder = 'Search items...', onSearch }) {
  const [query, setQuery] = useState('')

  const handleSubmit = (event) => {
    event.preventDefault()
    onSearch?.(query.trim())
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="glassmorphism dark:glassmorphism-dark border border-white/10 p-3 rounded-[28px] shadow-xl shadow-slate-950/30 flex flex-col sm:flex-row items-center gap-3 max-w-4xl mx-auto"
    >
      <label htmlFor="search-input" className="sr-only">
        {label}
      </label>
      <div className="flex items-center gap-3 w-full sm:w-auto px-4 py-3 rounded-[24px] bg-slate-950/10 dark:bg-slate-200/10 border border-white/10">
        <svg
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.8"
          strokeLinecap="round"
          strokeLinejoin="round"
          className="h-5 w-5 text-slate-200 dark:text-slate-100"
        >
          <circle cx="11" cy="11" r="7" />
          <path d="m21 21-4.3-4.3" />
        </svg>
        <input
          id="search-input"
          type="search"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder={placeholder}
          className="min-w-0 w-full bg-transparent outline-none text-slate-900 dark:text-slate-100 placeholder:text-slate-400 dark:placeholder:text-slate-500"
        />
      </div>
      <button
        type="submit"
        className="inline-flex items-center justify-center rounded-2xl bg-gradient-to-r from-dark-blue-600 to-purple-600 px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-dark-blue-600/30 transition-all duration-200 hover:brightness-110"
      >
        Search
      </button>
    </form>
  )
}

export default SearchBar
