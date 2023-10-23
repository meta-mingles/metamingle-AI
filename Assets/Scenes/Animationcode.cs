using System.Collections;
using System.Collections.Generic;
using System;
using System.Net;
using System.Net.Sockets;
using UnityEngine;
using System.Diagnostics;

public class Animationcode : MonoBehaviour
{
    public GameObject[] Body;

    private Socket clientSocket;

    private void Start()
    {
        Process psi = new Process();
        psi.StartInfo.FileName = System.Environment.GetEnvironmentVariable("PYTHONEXE_PATH");

        // ���̽� ȯ�� ����
        psi.StartInfo.FileName = System.Environment.GetEnvironmentVariable("MEDIAPIPE_PYTHON_PATH");
        

        // ������ ���̽� ����
        psi.StartInfo.CreateNoWindow = true;
        psi.StartInfo.UseShellExecute = false;
        psi.Start();
        UnityEngine.Debug.Log("����Ϸ�");

        clientSocket = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);
        IPAddress serverIP = IPAddress.Parse("127.0.0.1");
        IPEndPoint serverEndPoint = new IPEndPoint(serverIP, 12345);

        try
        {
            clientSocket.Connect(serverEndPoint);
            UnityEngine.Debug.Log("Connected to server");
        }
        catch (Exception e)
        {
            UnityEngine.Debug.LogError($"Error connecting to server: {e}");
            return;
        }
    }


    void Update()
    {
        int counter = 0;
        
        try
        {
            //����Ƽ�� �������� 
            string message = "Hello from Unity!";
            byte[] messageBytes = System.Text.Encoding.UTF8.GetBytes(message);
            clientSocket.Send(messageBytes);


            //���̽㿡�� �� �ޱ�
            byte[] buffer = new byte[1024];
            int receivedBytes = clientSocket.Receive(buffer);
            string receivedMessage = System.Text.Encoding.UTF8.GetString(buffer, 0, receivedBytes); //receivedMessage ���ڿ��ޱ�
            UnityEngine.Debug.Log($"Received from Python: {receivedMessage}");

            // ���ڿ����� ��ȣ �� ��ǥ�� ����
            receivedMessage = receivedMessage.Replace("[[", "").Replace("]]", "").Replace(", [", "");
            string[] coordinatePairs = receivedMessage.Split(new char[] { ']' }, StringSplitOptions.RemoveEmptyEntries);

            // �� ��ǥ ���� �ݺ��ϰ� x, y, z ���� ����
            foreach (string pair in coordinatePairs)
            {
                //UnityEngine.Debug.Log($"pair: {pair}");
                string[] coordinates = pair.Split(',');

                float x = float.Parse(coordinates[0]) / 200;
                float y = float.Parse(coordinates[1]) / 200;
                float z = float.Parse(coordinates[2]) / 200;
                UnityEngine.Debug.Log($"x: {x}, y: {y}, z: {z}");

                Body[counter].transform.localPosition = new Vector3(x, -y, z);
                counter += 1;

            }
        }
        catch (Exception e)
        {
            UnityEngine.Debug.LogError("[�˸�] �����߻�: " + e.Message);
            clientSocket.Shutdown(SocketShutdown.Both);
            clientSocket.Close();
        }
    }
}