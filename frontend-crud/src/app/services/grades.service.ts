import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Grade {
  id: number;
  student_id: number;
  name: string;
  subject: string;
  grade: number;
  grade_date: string;
  created_at: string;
}

export interface CreateGradeRequest {
  student_name: string;
  subject: string;
  grade: number;
  grade_date: string;
}

export interface UpdateGradeRequest {
  subject?: string;
  grade?: number;
  grade_date?: string;
}

export interface GradesResponse {
  success: boolean;
  data: Grade | Grade[];
  error?: string;
  errors?: string[];
}

@Injectable({
  providedIn: 'root'
})
export class GradesService {
  private apiUrl = 'http://localhost:5000/api';

  constructor(private http: HttpClient) { }

  /**
   * Recupera tutti i voti dal backend
   */
  getAllGrades(): Observable<GradesResponse> {
    return this.http.get<GradesResponse>(`${this.apiUrl}/grades`);
  }

  /**
   * Recupera un singolo voto per ID
   */
  getGradeById(id: number): Observable<GradesResponse> {
    return this.http.get<GradesResponse>(`${this.apiUrl}/grades/${id}`);
  }

  /**
   * Crea un nuovo voto
   */
  createGrade(gradeData: CreateGradeRequest): Observable<GradesResponse> {
    return this.http.post<GradesResponse>(`${this.apiUrl}/grades`, gradeData);
  }

  /**
   * Aggiorna un voto esistente
   */
  updateGrade(id: number, gradeData: UpdateGradeRequest): Observable<GradesResponse> {
    return this.http.put<GradesResponse>(`${this.apiUrl}/grades/${id}`, gradeData);
  }

  /**
   * Filtra i voti per nome studente
   */
  filterByStudentName(grades: Grade[], studentName: string): Grade[] {
    if (!studentName.trim()) {
      return grades;
    }
    return grades.filter(grade =>
      grade.name.toLowerCase().includes(studentName.toLowerCase())
    );
  }

  /**
   * Determina il colore del voto basato sul valore
   */
  getGradeColor(grade: number): string {
    return grade >= 6 ? 'grade-pass' : 'grade-fail';
  }

  /**
   * Verifica se il voto è insufficiente (< 6)
   */
  isFailingGrade(grade: number): boolean {
    return grade < 6;
  }
}
