from __future__ import annotations

from threading import Lock
from typing import Dict, List, Optional

from app.memory.models.episode import Episode


class EpisodicMemoryStore:
    """
    Stores completed conversation episodes.

    Episodes are indexed by their ID.
    """

    def __init__(self):
        self._episodes: Dict[str, Episode] = {}
        self._lock = Lock()

    def add(self, episode: Episode) -> None:
        with self._lock:
            self._episodes[episode.id] = episode

    def get(self, episode_id: str) -> Optional[Episode]:
        return self._episodes.get(episode_id)

    def remove(self, episode_id: str) -> bool:
        with self._lock:
            if episode_id in self._episodes:
                del self._episodes[episode_id]
                return True
            return False

    def update(self, episode: Episode) -> None:
        with self._lock:
            self._episodes[episode.id] = episode

    def get_all(self) -> List[Episode]:
        return list(self._episodes.values())

    def recent(self, limit: int = 10) -> List[Episode]:
        episodes = sorted(
            self._episodes.values(),
            key=lambda e: e.updated_at,
            reverse=True,
        )

        return episodes[:limit]

    def clear(self) -> None:
        with self._lock:
            self._episodes.clear()

    def size(self) -> int:
        return len(self._episodes)

    def exists(self, episode_id: str) -> bool:
        return episode_id in self._episodes

    def __len__(self):
        return len(self._episodes)

    def __iter__(self):
        return iter(self.get_all())