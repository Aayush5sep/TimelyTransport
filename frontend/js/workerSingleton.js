// workerSingleton.js
let sharedWorker;

// Function to get the shared worker instance
export function getSharedWorker() {
    if (!sharedWorker) {
        sharedWorker = new SharedWorker('js/worker.js');
    }
    return sharedWorker;
}