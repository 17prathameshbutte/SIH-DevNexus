import h5py
import numpy as np

class H5Inspector:
    def inspect(self, filepath: str) -> dict:
        result = {'groups': [], 'datasets': []}
        try:
            with h5py.File(filepath, 'r') as f:
                def visit_func(name, node):
                    if isinstance(node, h5py.Group):
                        result['groups'].append({
                            'path': name,
                            'attributes': {k: self._convert_val(v) for k, v in node.attrs.items()}
                        })
                    elif isinstance(node, h5py.Dataset):
                        sample = None
                        if node.shape and np.prod(node.shape) > 0:
                            sample = self._convert_val(node[:min(5, node.shape[0])])
                        result['datasets'].append({
                            'path': name,
                            'shape': node.shape,
                            'dtype': str(node.dtype),
                            'attributes': {k: self._convert_val(v) for k, v in node.attrs.items()},
                            'sample': sample
                        })
                f.visititems(visit_func)
        except Exception as e:
            return {'error': str(e)}
        return result

    def _convert_val(self, val):
        if isinstance(val, np.ndarray):
            return val.tolist()
        if isinstance(val, np.generic):
            return val.item()
        if isinstance(val, bytes):
            return val.decode('utf-8')
        return val
