"""
Variational Mode Decomposition (VMD) for time series decomposition.
"""
import numpy as np
from typing import Tuple, Optional
from scipy.signal import hilbert

from app.core import get_logger


logger = get_logger(__name__)


class VMDService:
    """
    Variational Mode Decomposition service.
    
    Decomposes time series into Intrinsic Mode Functions (IMFs).
    """
    
    def __init__(self):
        self.vmd_available = self._check_vmd_availability()
    
    def _check_vmd_availability(self) -> bool:
        """Check if VMD library is available."""
        try:
            import vmdpy
            return True
        except ImportError:
            logger.warning("vmdpy not available, using fallback EMD")
            return False
    
    def decompose(
        self,
        signal: np.ndarray,
        n_modes: int = 6,
        alpha: float = 2000,
        tau: float = 0,
        dc: int = 0,
        init: int = 1,
        tol: float = 1e-7
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Perform VMD decomposition.
        
        Args:
            signal: Input time series
            n_modes: Number of modes to extract (IMFs)
            alpha: Balancing parameter
            tau: Time-step of dual ascent
            dc: True if first mode should be constant (DC)
            init: Initialization method
            tol: Tolerance for convergence
        
        Returns:
            Tuple of (modes/IMFs, mode spectra, omega (central frequencies))
        """
        if self.vmd_available:
            return self._vmd_decomposition(signal, n_modes, alpha, tau, dc, init, tol)
        else:
            return self._fallback_emd_decomposition(signal, n_modes)
    
    def _vmd_decomposition(
        self,
        signal: np.ndarray,
        n_modes: int,
        alpha: float,
        tau: float,
        dc: int,
        init: int,
        tol: float
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """VMD decomposition using vmdpy library."""
        try:
            from vmdpy import VMD
            
            # Run VMD
            modes, mode_spectra, omega = VMD(
                signal,
                alpha=alpha,
                tau=tau,
                K=n_modes,
                DC=dc,
                init=init,
                tol=tol
            )
            
            logger.info(f"VMD decomposition completed: {n_modes} modes extracted")
            return modes, mode_spectra, omega
            
        except Exception as e:
            logger.error(f"VMD decomposition failed: {e}, using fallback")
            return self._fallback_emd_decomposition(signal, n_modes)
    
    def _fallback_emd_decomposition(
        self,
        signal: np.ndarray,
        n_modes: int
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Fallback EMD-like decomposition using Fourier decomposition.
        
        This is a simplified alternative when VMDpy is not available.
        """
        logger.info(f"Using fallback Fourier-based decomposition for {n_modes} modes")
        
        # Perform FFT
        fft = np.fft.fft(signal)
        freqs = np.fft.fftfreq(len(signal))
        
        # Split frequency bands logarithmically
        modes = np.zeros((n_modes, len(signal)))
        
        # Create frequency bands
        freq_bands = np.logspace(np.log10(0.001), np.log10(0.5), n_modes + 1)
        
        for i in range(n_modes):
            # Create band-pass filter
            mask = (np.abs(freqs) >= freq_bands[i]) & (np.abs(freqs) < freq_bands[i + 1])
            
            # Apply filter
            filtered_fft = fft.copy()
            filtered_fft[~mask] = 0
            
            # Inverse FFT
            modes[i] = np.real(np.fft.ifft(filtered_fft))
        
        # Mock mode spectra and omega
        mode_spectra = np.abs(fft)
        omega = freq_bands[:-1]
        
        logger.info(f"Fallback decomposition completed: {n_modes} modes extracted")
        return modes, mode_spectra, omega
    
    def cluster_modes(
        self,
        modes: np.ndarray,
        n_clusters: int = 3
    ) -> dict:
        """
        Cluster IMFs into high/mid/low frequency groups using K-means.
        
        Args:
            modes: Array of IMFs (n_modes, signal_length)
            n_clusters: Number of clusters (default 3 for high/mid/low)
        
        Returns:
            Dictionary with cluster assignments and grouped modes
        """
        from sklearn.cluster import KMeans
        
        # Calculate average frequency for each mode using zero-crossing
        frequencies = []
        for mode in modes:
            # Count zero crossings
            zero_crossings = np.where(np.diff(np.sign(mode)))[0]
            avg_freq = len(zero_crossings) / (2 * len(mode))
            frequencies.append(avg_freq)
        
        # Reshape for clustering
        freq_array = np.array(frequencies).reshape(-1, 1)
        
        # K-means clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(freq_array)
        
        # Sort clusters by frequency (0=low, 1=mid, 2=high)
        cluster_freqs = {i: np.mean(freq_array[labels == i]) for i in range(n_clusters)}
        sorted_clusters = sorted(cluster_freqs.items(), key=lambda x: x[1])
        
        # Map to low/mid/high
        cluster_mapping = {old: new for new, (old, _) in enumerate(sorted_clusters)}
        labels = np.array([cluster_mapping[label] for label in labels])
        
        # Group modes by cluster
        grouped_modes = {
            'low_freq': modes[labels == 0],
            'mid_freq': modes[labels == 1],
            'high_freq': modes[labels == 2] if n_clusters > 2 else np.array([])
        }
        
        logger.info(
            f"Clustered {len(modes)} modes into {n_clusters} groups: "
            f"low={len(grouped_modes['low_freq'])}, "
            f"mid={len(grouped_modes['mid_freq'])}, "
            f"high={len(grouped_modes['high_freq'])}"
        )
        
        return {
            'labels': labels,
            'grouped_modes': grouped_modes,
            'frequencies': frequencies
        }
    
    def reconstruct_signal(
        self,
        modes: np.ndarray
    ) -> np.ndarray:
        """
        Reconstruct original signal from IMFs.
        
        Args:
            modes: Array of IMFs
        
        Returns:
            Reconstructed signal
        """
        reconstructed = np.sum(modes, axis=0)
        return reconstructed


# Global instance
vmd_service = VMDService()
