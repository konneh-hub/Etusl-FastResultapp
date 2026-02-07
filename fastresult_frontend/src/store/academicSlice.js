import { createSlice } from '@reduxjs/toolkit'

const academicSlice = createSlice({
  name: 'academic',
  initialState: {
    academic_years: [],
    semesters: [],
    universities: [],
    loading: false
  },
  reducers: {
    setAcademicYears: (state, action) => {
      state.academic_years = action.payload
    },
    setSemesters: (state, action) => {
      state.semesters = action.payload
    },
    setUniversities: (state, action) => {
      state.universities = action.payload
    },
    setLoading: (state, action) => {
      state.loading = action.payload
    }
  }
})

export const { setAcademicYears, setSemesters, setUniversities, setLoading } = academicSlice.actions
export default academicSlice.reducer
