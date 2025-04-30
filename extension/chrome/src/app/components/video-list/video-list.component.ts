import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { VideoInfo } from '../../../shared/models/video.model';

@Component({
  selector: 'app-video-list',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="video-list">
      <div *ngFor="let video of videos" class="video-item">
        <div class="video-thumbnail">
          <!-- Placeholder for thumbnail -->
          <div class="thumbnail-placeholder">
            <span class="video-icon">🎬</span>
          </div>
        </div>
        
        <div class="video-details">
          <div class="video-title">{{ getVideoTitle(video) }}</div>
          
          <div class="video-metadata">
            <span *ngIf="video.duration && video.duration > 0" class="video-duration">
              {{ formatDuration(video.duration) }}
            </span>
            
            <span *ngIf="video.dimensions && video.dimensions.width && video.dimensions.height" class="video-resolution">
              {{ video.dimensions.width }}x{{ video.dimensions.height }}
            </span>
          </div>
        </div>
        
        <div class="video-actions">
          <button class="download-btn" (click)="onDownload(video)" title="Download Video">
            <span class="icon">⬇️</span>
          </button>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .video-list {
      flex: 1;
      overflow-y: auto;
      padding: 8px;
    }
    
    .video-item {
      display: flex;
      margin-bottom: 12px;
      padding: 12px;
      background-color: #f5f5f5;
      border-radius: 8px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .video-thumbnail {
      width: 80px;
      height: 60px;
      margin-right: 12px;
      flex-shrink: 0;
    }
    
    .thumbnail-placeholder {
      width: 100%;
      height: 100%;
      background-color: #ddd;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 4px;
    }
    
    .video-icon {
      font-size: 24px;
    }
    
    .video-details {
      flex: 1;
      min-width: 0;
      display: flex;
      flex-direction: column;
    }
    
    .video-title {
      font-size: 14px;
      font-weight: 500;
      margin-bottom: 4px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    
    .video-metadata {
      display: flex;
      gap: 8px;
      font-size: 12px;
      color: #666;
    }
    
    .video-actions {
      display: flex;
      align-items: center;
      margin-left: 8px;
    }
    
    .download-btn {
      background: transparent;
      border: none;
      cursor: pointer;
      padding: 4px;
      font-size: 16px;
      border-radius: 4px;
      transition: background-color 0.2s;
    }
    
    .download-btn:hover {
      background-color: rgba(0,0,0,0.05);
    }
  `]
})
export class VideoListComponent {
  @Input() videos: VideoInfo[] = [];
  @Output() download = new EventEmitter<VideoInfo>();
  
  onDownload(video: VideoInfo): void {
    this.download.emit(video);
  }
  
  getVideoTitle(video: VideoInfo): string {
    return video.filename || 'Unknown Video';
  }
  
  formatDuration(seconds: number): string {
    if (!seconds || seconds <= 0) return '';
    
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    
    if (hrs > 0) {
      return `${hrs}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    } else {
      return `${mins}:${secs.toString().padStart(2, '0')}`;
    }
  }
} 