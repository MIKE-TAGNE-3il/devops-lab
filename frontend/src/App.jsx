import { useEffect, useState } from 'react'
import './App.css'

// Adresse RELATIVE : même domaine que la page, donc pas de CORS, et la même application
// fonctionne partout (Nginx en local, Traefik en production) sans être reconstruite.
const API = '/api/items'

// Appel HTTP commun : transforme une réponse d'erreur (4xx/5xx) en exception.
async function request(url, options) {
  const response = await fetch(url, options)
  if (!response.ok) throw new Error(`L'API a répondu ${response.status}`)
  // 204 = succès sans contenu (cas du DELETE) : il n'y a rien à lire.
  return response.status === 204 ? null : response.json()
}

export default function App() {
  const [items, setItems] = useState([])
  const [name, setName] = useState('')
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)

  async function load() {
    try {
      setItems(await request(API))
      setError(null)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  // Chargement initial : [] = une seule fois, au premier affichage.
  useEffect(() => {
    // Faux positif de la règle : load() n'appelle setItems qu'APRÈS le "await" du fetch,
    // donc jamais de façon synchrone (le cas qui provoque des rendus en cascade).
    // eslint-disable-next-line react-hooks/set-state-in-effect
    load()
  }, [])

  async function add(event) {
    event.preventDefault()
    try {
      await request(API, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name }),
      })
      setName('')
      await load()
    } catch (e) {
      setError(e.message)
    }
  }

  async function remove(id) {
    try {
      await request(`${API}/${id}`, { method: 'DELETE' })
      await load()
    } catch (e) {
      setError(e.message)
    }
  }

  return (
    <main>
      <h1>DevOps Lab</h1>

      <form onSubmit={add}>
        {/* maxLength reprend la limite de l'API (100) : la validation reste côté serveur. */}
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Nom de l'élément"
          maxLength={100}
          required
        />
        <button type="submit">Ajouter</button>
      </form>

      {error && <p className="error">{error}</p>}
      {loading && <p>Chargement…</p>}

      <ul>
        {items.map((item) => (
          <li key={item.id}>
            {/* React échappe le texte affiché : un nom contenant du HTML reste du texte (anti-XSS). */}
            <span>{item.name}</span>
            <small>{new Date(item.created_at).toLocaleString('fr-FR')}</small>
            <button onClick={() => remove(item.id)}>Supprimer</button>
          </li>
        ))}
      </ul>

      {!loading && !error && items.length === 0 && <p>Aucun élément pour le moment.</p>}
    </main>
  )
}
