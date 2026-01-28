import { Component, OnInit, signal } from '@angular/core';
import { RouterOutlet, CommonModule } from '@angular/router';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { GradesService, Grade, CreateGradeRequest, UpdateGradeRequest } from './services/grades.service';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, CommonModule, FormsModule, ReactiveFormsModule],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App implements OnInit {
  protected readonly title = signal('frontend-crud');

  // Signals per lo stato del componente
  allGrades = signal<Grade[]>([]);
  filteredGrades = signal<Grade[]>([]);
  studentNameFilter = signal('');
  isLoading = signal(false);
  errorMessage = signal('');
  successMessage = signal('');

  // Form per inserimento
  showInsertForm = signal(false);
  insertFormData = signal({
    student_name: '',
    subject: '',
    grade: '',
    grade_date: this.getTodayDate()
  });
  insertFormErrors = signal<string[]>([]);

  // Form per modifica
  showEditForm = signal(false);
  editingGradeId = signal<number | null>(null);
  editFormData = signal({
    subject: '',
    grade: '',
    grade_date: ''
  });
  editFormErrors = signal<string[]>([]);

  constructor(private gradesService: GradesService) { }

  ngOnInit(): void {
    this.loadGrades();
  }

  /**
   * Carica tutti i voti dal backend
   */
  loadGrades(): void {
    this.isLoading.set(true);
    this.errorMessage.set('');
    this.successMessage.set('');

    this.gradesService.getAllGrades().subscribe({
      next: (response) => {
        if (response.success && Array.isArray(response.data)) {
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
   * Mostra il form di inserimento
   */
  openInsertForm(): void {
    this.showInsertForm.set(true);
    this.insertFormData.set({
      student_name: '',
      subject: '',
      grade: '',
      grade_date: this.getTodayDate()
    });
    this.insertFormErrors.set([]);
  }

  /**
   * Chiude il form di inserimento
   */
  closeInsertForm(): void {
    this.showInsertForm.set(false);
    this.insertFormErrors.set([]);
  }

  /**
   * Invia il form di inserimento
   */
  submitInsertForm(): void {
    const data = this.insertFormData();
    
    const gradeData: CreateGradeRequest = {
      student_name: data.student_name,
      subject: data.subject,
      grade: parseInt(data.grade),
      grade_date: data.grade_date
    };

    this.gradesService.createGrade(gradeData).subscribe({
      next: (response) => {
        if (response.success) {
          this.successMessage.set('Voto inserito con successo!');
          this.closeInsertForm();
          this.loadGrades();
          setTimeout(() => this.successMessage.set(''), 3000);
        } else {
          this.insertFormErrors.set(response.errors || [response.error || 'Errore sconosciuto']);
        }
      },
      error: (error) => {
        console.error('Errore nell\'inserimento:', error);
        this.insertFormErrors.set(['Errore nella comunicazione con il server']);
      }
    });
  }

  /**
   * Apre il form di modifica per un voto
   */
  openEditForm(grade: Grade): void {
    this.editingGradeId.set(grade.id);
    this.editFormData.set({
      subject: grade.subject,
      grade: grade.grade.toString(),
      grade_date: grade.grade_date
    });
    this.showEditForm.set(true);
    this.editFormErrors.set([]);
  }

  /**
   * Chiude il form di modifica
   */
  closeEditForm(): void {
    this.showEditForm.set(false);
    this.editingGradeId.set(null);
    this.editFormErrors.set([]);
  }

  /**
   * Invia il form di modifica
   */
  submitEditForm(): void {
    const gradeId = this.editingGradeId();
    if (!gradeId) return;

    const data = this.editFormData();
    
    const updateData: UpdateGradeRequest = {
      subject: data.subject,
      grade: data.grade ? parseInt(data.grade) : undefined,
      grade_date: data.grade_date
    };

    this.gradesService.updateGrade(gradeId, updateData).subscribe({
      next: (response) => {
        if (response.success) {
          this.successMessage.set('Voto aggiornato con successo!');
          this.closeEditForm();
          this.loadGrades();
          setTimeout(() => this.successMessage.set(''), 3000);
        } else {
          this.editFormErrors.set(response.errors || [response.error || 'Errore sconosciuto']);
        }
      },
      error: (error) => {
        console.error('Errore nella modifica:', error);
        this.editFormErrors.set(['Errore nella comunicazione con il server']);
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
   * Verifica se il voto è insufficiente
   */
  isFailingGrade(grade: number): boolean {
    return this.gradesService.isFailingGrade(grade);
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

  /**
   * Restituisce la data odierna nel formato YYYY-MM-DD
   */
  private getTodayDate(): string {
    const today = new Date();
    return today.toISOString().split('T')[0];
  }
}
