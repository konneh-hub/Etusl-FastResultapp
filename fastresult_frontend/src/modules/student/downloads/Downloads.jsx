import React, { useCallback } from 'react';
import Table from '../../../../components/Table/Table';
import useApi from '../../../../hooks/useApi';
import * as filesService from '../../../../services/filesService';
import toast from 'react-hot-toast';
import './Downloads.css';

export default function Downloads() {
  const fetchDownloads = useCallback(async () => {
    return { results: [] };
  }, []);
  const { data: resp, loading } = useApi(fetchDownloads, []);
  const downloads = resp?.results || resp || [];

  const handleDownload = async (item) => {
    try {
      const blob = await filesService.downloadFile(item.id);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = item.name;
      link.click();
      toast.success('File downloaded');
    } catch (error) {
      toast.error('Failed to download file');
    }
  };

  return (
    <div className="downloads">
      <h1>Downloads</h1>

      <Table
        data={downloads}
        columns={[
          { key: 'name', label: 'File Name' },
          { key: 'type', label: 'Type' },
          { key: 'size', label: 'Size' },
          { key: 'uploadDate', label: 'Date' },
          { key: 'actions', label: 'Actions', render: (_, row) => (
            <button onClick={() => handleDownload(row)}>Download</button>
          )}
        ]}
        loading={loading}
      />
    </div>
  );
}
