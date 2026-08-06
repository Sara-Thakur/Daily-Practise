import { useState } from 'react'
import Chat from './Chat.tsx'

import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
    <Chat></Chat>
      <section id="center">
        <div>
          <p>
            Edit <code>src/App.tsx</code> and save to test <code>HMR</code>
          </p>
        </div>
        <button
          type="button"
          className="counter"
          onClick={() => setCount((count) => count + 1)}
        >
          Count is {count}
        </button>
      </section>

      <div className="ticks"></div>

    </>
  )
}

export default App
