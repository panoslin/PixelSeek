import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SidebarComponent } from './components/sidebar/sidebar.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, SidebarComponent],
  template: `
    <app-sidebar></app-sidebar>
  `,
  styles: [`
    :host {
      display: block;
      height: 100%;
      width: 100%;
    }
  `]
})
export class AppComponent {
  title = 'PixelSeek Extension - Hello World!';
  currentYear = new Date().getFullYear();
} 