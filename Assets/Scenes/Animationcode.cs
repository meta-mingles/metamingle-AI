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

    string pythonExePath;

    private void Start()
    {

        Process psi = new Process();

        psi.StartInfo.FileName = "C:/Users/user/miniconda3/envs/mmpose/python.exe";
        // 파이썬 환경 연결
        psi.StartInfo.Arguments = "D:/Meta_Final_Project/metamingle-AI3/Assets/Scenes/socket_pose_cvzone.py";
        // 실행할 파이썬 파일



        psi.StartInfo.CreateNoWindow = true;
        psi.StartInfo.UseShellExecute = false;
        psi.Start();
        UnityEngine.Debug.Log("실행완료");

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
            //유니티에 값보내기 
            string message = "Hello from Unity!";
            byte[] messageBytes = System.Text.Encoding.UTF8.GetBytes(message);
            clientSocket.Send(messageBytes);


            //파이썬에서 값 받기
            byte[] buffer = new byte[1024];
            int receivedBytes = clientSocket.Receive(buffer);
            string receivedMessage = System.Text.Encoding.UTF8.GetString(buffer, 0, receivedBytes); //receivedMessage 문자열받기
            UnityEngine.Debug.Log($"Received from Python: {receivedMessage}");

            // 문자열에서 괄호 및 쉼표를 제거
            receivedMessage = receivedMessage.Replace("[[", "").Replace("]]", "").Replace(", [", "");
            string[] coordinatePairs = receivedMessage.Split(new char[] { ']' }, StringSplitOptions.RemoveEmptyEntries);

            // 각 좌표 쌍을 반복하고 x, y, z 값을 추출
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
            UnityEngine.Debug.LogError("[알림] 에러발생: " + e.Message);
            clientSocket.Shutdown(SocketShutdown.Both);
            clientSocket.Close();
        }
    }
}