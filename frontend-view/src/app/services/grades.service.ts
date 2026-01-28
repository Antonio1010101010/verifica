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

export interface GradesResponse {
  success: boolean;
  data: Grade[];
  error?: string;
}

@Injectable({
  providedIn: 'root'
})
export class GradesService {
  private apiUrl = 'http://localhost:5000/api';

  constructor(private http: HttpClient) { }

  /**
   * Recupera tutti i voti dal backend
   * @returns Observable<GradesResponse>
   */
  getAllGrades(): Observable<GradesResponse> {
    return this.http.get<GradesResponse>(`${this.apiUrl}/grades`);
  }

  /**
   * Filtra i voti per nome studente
   * @param grades - Lista di voti
   * @param studentName - Nome dello studente da cercare
   * @returns Voti dello studente
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
   * @param grade - Valore del voto
   * @returns Classe CSS 'grade-pass' (verde) o 'grade-fail' (rosso)
   */
  getGradeColor(grade: number): string {
    return grade >= 6 ? 'grade-pass' : 'grade-fail';
  }
}
