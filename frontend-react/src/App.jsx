import { NavLink, Routes, Route, Navigate } from 'react-router-dom'
import './App.css'
import ManhwaPage from './Manhwa/ManhwaPage'
import JAVPage from './JAV/JAVPage'
import ManhwaDetail from './Manhwa/Pages/ManhwaDetail'
import ChapterDetail from './Manhwa/Pages/ChapterDetail'
import JAVDetails from './JAV/Pages/JAVDetails'

function App() {
  return (
    <div className="App">
      <div className="min-h-screen bg-gradient-to-br from-black via-zinc-900 to-zinc-950 text-white p-6">

     

        <div className="mt-6">
          <Routes>
            <Route path="/" element={<Navigate replace to="/manhwa" />} />
            <Route path="/manhwa" element={<ManhwaPage />} />
            <Route path='/manhwa/details/:slug' element={<ManhwaDetail></ManhwaDetail>}/>
            <Route path='/manhwa/:slug/chapter/:chapter_number' element={<ChapterDetail></ChapterDetail>}/>
            <Route path="/jav" element={<JAVPage />} />
            <Route path="/jav/:dvd_id" element={<JAVDetails />} />
            <Route path="*" element={<Navigate replace to="/manhwa" />} />
          </Routes>
        </div>

      </div>
    </div>
  )
}

export default App
