const timestamp_format = (timestamp) => {
    const date = new Date(timestamp);
    const pad = (n) => n.toString().padStart(2, '0');
    const MM = pad(date.getMonth() + 1);
    const DD = pad(date.getDate());
    const HH = pad(date.getHours());
    const mm = pad(date.getMinutes());
    const ss = pad(date.getSeconds());

    return `${MM}-${DD} ${HH}:${mm}:${ss}`;
}

export { timestamp_format }