import { Component, OnInit, signal } from '@angular/core';
import { RouterOutlet, CommonModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { GradesService, Grade } from './services/grades.service';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, CommonModule, FormsModule],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App implements OnInit {
  protected readonly title = signal('frontend-view');
  
  // Signals per lo stato del componente
  allGrades = signal<Grade[]>([]);
  filteredGrades = signal<Grade[]>([]);
  studentNameFilter = signal('');
  isLoading = signal(false);
  errorMessage = signal('');

  constructor(private gradesService: GradesService) {}

  ngOnInit(): void {
    this.loadGrades();
  }

  /**
   * Carica tutti i voti dal backend
   */
  loadGrades(): void {
    this.isLoading.set(true);
    this.errorMessage.set('');

    this.gradesService.getAllGrades().subscribe({
      next: (response) => {
        if (response.success && response.data) {
          this.allGrades.set(response.data);
          this.applyFilter();
        } else {
          this.errorMessage.set('Errore nel caricamento dei voti');
        }
        this.isLoading.set(false);
      },
      error: (error) => {
        console.error('Errore nel caricamento dei voti:', error);
        this.errorMessage.set('Impossibile contattare il server');
        this.isLoading.set(false);
      }
    });
  }

  /**
   * Filtra i voti in base al nome dello studente
   */
  onFilterChange(): void {
    this.applyFilter();
  }

  /**
   * Applica il filtro ai voti
   */
  private applyFilter(): void {
    const filtered = this.gradesService.filterByStudentName(
      this.allGrades(),
      this.studentNameFilter()
    );
    this.filteredGrades.set(filtered);
  }

  /**
   * Determina la classe CSS per il colore del voto
   */
  getGradeColor(grade: number): string {
    return this.gradesService.getGradeColor(grade);
  }

  /**
   * Verifica se il voto è insufficiente (< 6)
   */
  isFailingGrade(grade: number): boolean {
    return grade < 6;
  }

  /**
   * Formatta la data per la visualizzazione
   */
  formatDate(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleDateString('it-IT', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  }
}
