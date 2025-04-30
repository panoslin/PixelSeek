import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { VideoService } from '../../services/video.service';
import { VideoInfo } from '../../../shared/models/video.model';
import { VideoListComponent } from '../video-list/video-list.component';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [CommonModule, VideoListComponent],
  template: `
    <div class="sidebar-container">
      <header class="sidebar-header">
        <h1>PixelSeek</h1>
        <div class="actions">
          <button class="refresh-btn" (click)="refreshVideos()" title="Refresh Videos">
            <span class="icon">🔄</span>
          </button>
        </div>
      </header>
      
      <app-video-list 
        [videos]="videos" 
        (download)="downloadVideo($event)">
      </app-video-list>
      
      <div *ngIf="loading" class="loading-indicator">
        Loading videos...
      </div>
      
      <div *ngIf="!loading && videos.length === 0" class="empty-state">
        No videos detected on this page. 
        Try playing a video or refreshing.
      </div>
    </div>
  `,
  styles: [`
    .sidebar-container {
      display: flex;
      flex-direction: column;
      height: 100vh;
      overflow: hidden;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .sidebar-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 12px 16px;
      background-color: #2c2c2c;
      color: white;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .sidebar-header h1 {
      margin: 0;
      font-size: 18px;
      font-weight: 500;
    }
    
    .actions {
      display: flex;
      gap: 8px;
    }
    
    .refresh-btn {
      background: transparent;
      border: none;
      color: white;
      font-size: 16px;
      cursor: pointer;
      padding: 4px 8px;
      border-radius: 4px;
      transition: background-color 0.2s;
    }
    
    .refresh-btn:hover {
      background-color: rgba(255,255,255,0.1);
    }
    
    .loading-indicator {
      padding: 16px;
      text-align: center;
      color: #666;
    }
    
    .empty-state {
      padding: 24px 16px;
      text-align: center;
      color: #666;
      font-size: 14px;
      line-height: 1.5;
    }
  `]
})
export class SidebarComponent implements OnInit {
  videos: VideoInfo[] = [];
  loading = true;
  
  constructor(private videoService: VideoService) {}
  
  ngOnInit(): void {
    // Subscribe to videos from the service
    this.videoService.videos$.subscribe(videos => {
      this.videos = videos;
      this.loading = false;
    });
    
    // Initial load of videos
    this.refreshVideos();
  }
  
  refreshVideos(): void {
    this.loading = true;
    this.videoService.forceCheckVideos()
      .then(() => {
        this.videoService.loadVideos();
        // Loading flag will be turned off when videos$ emits
      })
      .catch(() => {
        this.loading = false;
      });
  }
  
  downloadVideo(video: VideoInfo): void {
    this.videoService.downloadVideo(video)
      .then(() => {
        // Show success notification if needed
      })
      .catch(error => {
        console.error('Download failed:', error);
        // Show error notification if needed
      });
  }
} 