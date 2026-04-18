'use client'

import { useEffect, useState } from 'react'
import { supabase, Profile } from '@/lib/supabase'
import { User, Save, Plus, X } from 'lucide-react'

export default function ProfilePage() {
  const [profile, setProfile] = useState<Profile | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const [newSkill, setNewSkill] = useState('')
  const [newRole, setNewRole] = useState('')

  async function loadProfile() {
    const { data } = await supabase.from('profiles').select('*').eq('id', '00000000-0000-0000-0000-000000000001').single()
    setProfile(data)
    setLoading(false)
  }

  useEffect(() => { loadProfile() }, [])

  async function saveProfile() {
    if (!profile) return
    setSaving(true)
    await supabase.from('profiles').update(profile).eq('id', '00000000-0000-0000-0000-000000000001')
    setSaving(false)
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  function removeTag(field: keyof Profile, value: string) {
    if (!profile) return
    const arr = profile[field] as string[]
    setProfile({ ...profile, [field]: arr.filter(v => v !== value) })
  }

  function addTag(field: keyof Profile, value: string, setter: (v: string) => void) {
    if (!profile || !value.trim()) return
    const arr = profile[field] as string[]
    if (!arr.includes(value.trim())) {
      setProfile({ ...profile, [field]: [...arr, value.trim()] })
    }
    setter('')
  }

  if (loading || !profile) return <div className="text-gray-400 p-8">Loading profile...</div>

  return (
    <div className="space-y-6 animate-fade-in max-w-2xl">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-indigo-600/20 border border-indigo-600/30 flex items-center justify-center">
          <User size={18} className="text-indigo-400" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-white">Profile</h1>
          <p className="text-gray-400 text-sm">Your info used in every email</p>
        </div>
      </div>

      {/* Personal Info */}
      <div className="card p-5 space-y-4">
        <h2 className="text-sm font-semibold text-gray-300">Personal Information</h2>
        {[
          { label: 'Full Name', key: 'full_name' },
          { label: 'Primary Email (Company)', key: 'primary_email' },
          { label: 'Research Email (Professors)', key: 'research_email' },
          { label: 'Phone', key: 'phone' },
          { label: 'Location', key: 'location' },
          { label: 'Degree', key: 'degree' },
          { label: 'CGPA', key: 'cgpa' },
          { label: 'Portfolio URL', key: 'portfolio_url' },
          { label: 'GitHub URL', key: 'github_url' },
        ].map(({ label, key }) => (
          <div key={key}>
            <label className="text-xs text-gray-500 mb-1 block">{label}</label>
            <input
              type="text"
              value={(profile[key as keyof Profile] as string) ?? ''}
              onChange={e => setProfile({ ...profile, [key]: e.target.value })}
              className="w-full px-3 py-2 text-sm bg-[#0a0a0f] border border-[#1a1a35] rounded-lg text-white focus:border-indigo-500 outline-none transition-colors"
            />
          </div>
        ))}
      </div>

      {/* Target Roles */}
      <div className="card p-5 space-y-3">
        <h2 className="text-sm font-semibold text-gray-300">Target Roles</h2>
        <div className="flex flex-wrap gap-2">
          {profile.target_roles.map(role => (
            <span key={role} className="flex items-center gap-1 text-xs bg-indigo-600/20 text-indigo-300 border border-indigo-600/30 px-2.5 py-1 rounded-full">
              {role}
              <button onClick={() => removeTag('target_roles', role)}><X size={11} /></button>
            </span>
          ))}
        </div>
        <div className="flex gap-2">
          <input type="text" placeholder="Add role..." value={newRole} onChange={e => setNewRole(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && addTag('target_roles', newRole, setNewRole)}
            className="flex-1 px-3 py-1.5 text-sm bg-[#0a0a0f] border border-[#1a1a35] rounded-lg text-white focus:border-indigo-500 outline-none" />
          <button onClick={() => addTag('target_roles', newRole, setNewRole)}
            className="px-3 py-1.5 bg-indigo-600 rounded-lg text-white text-sm hover:bg-indigo-500"><Plus size={14} /></button>
        </div>
      </div>

      {/* Skills */}
      <div className="card p-5 space-y-4">
        <h2 className="text-sm font-semibold text-gray-300">Skills</h2>
        {[
          { label: 'Frontend', key: 'skills_frontend' },
          { label: 'Backend', key: 'skills_backend' },
          { label: 'Embedded', key: 'skills_embedded' },
          { label: 'Tools', key: 'skills_tools' },
        ].map(({ label, key }) => (
          <div key={key}>
            <p className="text-xs text-gray-500 mb-2">{label}</p>
            <div className="flex flex-wrap gap-2">
              {(profile[key as keyof Profile] as string[]).map(skill => (
                <span key={skill} className="flex items-center gap-1 text-xs bg-[#1a1a35] text-gray-300 px-2.5 py-1 rounded-full">
                  {skill}
                  <button onClick={() => removeTag(key as keyof Profile, skill)}><X size={11} className="text-gray-500 hover:text-red-400" /></button>
                </span>
              ))}
            </div>
          </div>
        ))}
        <div className="flex gap-2">
          <input type="text" placeholder="Add skill (e.g. React.js)..." value={newSkill} onChange={e => setNewSkill(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && addTag('skills_tools', newSkill, setNewSkill)}
            className="flex-1 px-3 py-1.5 text-sm bg-[#0a0a0f] border border-[#1a1a35] rounded-lg text-white focus:border-indigo-500 outline-none" />
          <button onClick={() => addTag('skills_tools', newSkill, setNewSkill)}
            className="px-3 py-1.5 bg-indigo-600 rounded-lg text-white text-sm hover:bg-indigo-500"><Plus size={14} /></button>
        </div>
      </div>

      {/* Resume Text */}
      <div className="card p-5">
        <h2 className="text-sm font-semibold text-gray-300 mb-3">Resume Text</h2>
        <p className="text-xs text-gray-500 mb-2">Paste your resume text here — used by AI to personalise emails</p>
        <textarea
          value={profile.resume_text ?? ''}
          onChange={e => setProfile({ ...profile, resume_text: e.target.value })}
          rows={10}
          className="w-full px-3 py-2 text-sm bg-[#0a0a0f] border border-[#1a1a35] rounded-lg text-white focus:border-indigo-500 outline-none resize-none font-mono"
          placeholder="Paste your resume text here..."
        />
      </div>

      <button onClick={saveProfile} disabled={saving}
        className={`w-full py-3 rounded-xl text-sm font-medium flex items-center justify-center gap-2 transition-all ${saved ? 'bg-green-600 text-white' : 'bg-indigo-600 hover:bg-indigo-500 text-white disabled:opacity-50'}`}>
        <Save size={16} />
        {saved ? '✓ Saved!' : saving ? 'Saving...' : 'Save Profile'}
      </button>
    </div>
  )
}
